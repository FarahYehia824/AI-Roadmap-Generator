"""
retriever.py
────────────
User query  →  Embed  →  Search ChromaDB  →  Return ranked context

Run standalone to test:
    python -m pipeline.retriever
"""

import os
from dataclasses import dataclass, field

import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sentence_transformers import SentenceTransformer

load_dotenv()
console = Console()

# ── Config ────────────────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
EMBEDDING_MODEL    = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
TOP_K              = int(os.getenv("TOP_K_RESULTS", 5))

COLLECTION_SKILLS    = "skills"
COLLECTION_ROADMAPS  = "roadmaps"
COLLECTION_RESOURCES = "resources"


# ── Data classes ──────────────────────────────────────────────────────────────
@dataclass
class RetrievedChunk:
    """One result from ChromaDB search."""
    text      : str
    metadata  : dict
    score     : float          # cosine similarity (higher = more relevant)
    chunk_type: str            # "skill" | "roadmap_step" | "resource"


@dataclass
class RetrievalResult:
    """Full retrieval result — passed to generator.py."""
    query          : str
    skills         : list[RetrievedChunk] = field(default_factory=list)
    roadmap_steps  : list[RetrievedChunk] = field(default_factory=list)
    resources      : list[RetrievedChunk] = field(default_factory=list)

    # ── helpers ───────────────────────────────────────────────────────────────
    def all_chunks(self) -> list[RetrievedChunk]:
        return self.skills + self.roadmap_steps + self.resources

    def as_context_string(self) -> str:
        """
        Flatten everything into one big context block for the LLM prompt.
        Format:
            === RELEVANT SKILLS ===
            ...chunks...

            === ROADMAP STEPS ===
            ...chunks...

            === RECOMMENDED RESOURCES ===
            ...chunks...
        """
        parts = []

        if self.skills:
            parts.append("=== RELEVANT SKILLS ===")
            for c in self.skills:
                parts.append(c.text)
                parts.append("")          # blank line between chunks

        if self.roadmap_steps:
            parts.append("=== ROADMAP STEPS ===")
            for c in self.roadmap_steps:
                parts.append(c.text)
                parts.append("")

        if self.resources:
            parts.append("=== RECOMMENDED RESOURCES ===")
            for c in self.resources:
                parts.append(c.text)
                parts.append("")

        return "\n".join(parts).strip()


# ── Retriever class ───────────────────────────────────────────────────────────
class Retriever:
    """
    Loads the embedding model + ChromaDB once, then answers queries fast.
    Designed to be instantiated once and reused (e.g. inside Streamlit).
    """

    def __init__(self):
        logger.info("Initialising Retriever ...")

        # Embedding model
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        logger.success(f"Embedding model loaded: {EMBEDDING_MODEL}")

        # ChromaDB client + collections
        self.client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
        self.col_skills    = self.client.get_collection(COLLECTION_SKILLS)
        self.col_roadmaps  = self.client.get_collection(COLLECTION_ROADMAPS)
        self.col_resources = self.client.get_collection(COLLECTION_RESOURCES)
        logger.success("ChromaDB collections loaded.")

    # ── Core search ───────────────────────────────────────────────────────────
    def _embed(self, text: str) -> list[float]:
        """Embed a single query string."""
        return self.model.encode(text, convert_to_tensor=False).tolist()

    def _search(
        self,
        collection: chromadb.Collection,
        query_vector: list[float],
        top_k: int,
        chunk_type: str,
        where: dict | None = None,          # optional metadata filter
    ) -> list[RetrievedChunk]:
        """
        Query one ChromaDB collection and return RetrievedChunk objects.
        ChromaDB returns distances (lower = closer); we convert to similarity.
        """
        kwargs = dict(
            query_embeddings=[query_vector],
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        if where:
            kwargs["where"] = where

        results = collection.query(**kwargs)

        chunks = []
        docs      = results["documents"][0]
        metas     = results["metadatas"][0]
        distances = results["distances"][0]

        for doc, meta, dist in zip(docs, metas, distances):
            # cosine distance → similarity score  (1 = identical, 0 = orthogonal)
            score = round(1 - dist, 4)
            chunks.append(RetrievedChunk(
                text=doc,
                metadata=meta,
                score=score,
                chunk_type=chunk_type,
            ))

        return chunks

    # ── Public API ────────────────────────────────────────────────────────────
    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K,
        level_filter: str | None = None,    # "Beginner" | "Intermediate" | "Advanced"
        track_filter: str | None = None,    # e.g. "Data Science & ML"
    ) -> RetrievalResult:
        """
        Main entry point.

        1. Embed the query.
        2. Search all 3 collections in parallel.
        3. Optionally filter by level or track.
        4. Return a RetrievalResult ready for the generator.
        """
        logger.info(f'Retrieving for query: "{query}"')

        query_vector = self._embed(query)

        # ── Optional filters ──────────────────────────────────────────────────
        skill_filter    = None
        roadmap_filter  = None
        resource_filter = None

        if level_filter:
            skill_filter    = {"level": level_filter}
            roadmap_filter  = {"level": level_filter}
            resource_filter = {"level": level_filter}

        if track_filter:
            roadmap_filter = {
                **(roadmap_filter or {}),
                "track": track_filter,
            }

        # ── Search ────────────────────────────────────────────────────────────
        skill_chunks    = self._search(self.col_skills,   query_vector, top_k, "skill",        skill_filter)
        roadmap_chunks  = self._search(self.col_roadmaps, query_vector, top_k, "roadmap_step", roadmap_filter)
        resource_chunks = self._search(self.col_resources,query_vector, top_k, "resource",     resource_filter)

        # ── Sort each group by score descending ───────────────────────────────
        skill_chunks    = sorted(skill_chunks,    key=lambda c: c.score, reverse=True)
        roadmap_chunks  = sorted(roadmap_chunks,  key=lambda c: c.score, reverse=True)
        resource_chunks = sorted(resource_chunks, key=lambda c: c.score, reverse=True)

        result = RetrievalResult(
            query=query,
            skills=skill_chunks,
            roadmap_steps=roadmap_chunks,
            resources=resource_chunks,
        )

        logger.success(
            f"Retrieved {len(skill_chunks)} skills | "
            f"{len(roadmap_chunks)} roadmap steps | "
            f"{len(resource_chunks)} resources"
        )
        return result


# ── Pretty-print helpers (for testing) ───────────────────────────────────────
def _print_results(result: RetrievalResult) -> None:
    console.print()
    console.rule(f'[bold cyan]Results for: "{result.query}"[/bold cyan]')

    for group_name, chunks in [
        ("🧠 Skills",          result.skills),
        ("🗺️  Roadmap Steps",  result.roadmap_steps),
        ("📚 Resources",       result.resources),
    ]:
        table = Table(title=group_name, show_lines=True, expand=True)
        table.add_column("Score", style="green", width=7)
        table.add_column("Chunk", style="white")
        table.add_column("Metadata", style="dim", width=30)

        for c in chunks:
            meta_str = "\n".join(f"{k}: {v}" for k, v in c.metadata.items()
                                 if k not in ("type",))
            table.add_row(str(c.score), c.text[:300] + "...", meta_str)

        console.print(table)
        console.print()

    # Context string preview
    console.print(Panel(
        result.as_context_string()[:800] + "\n\n[dim]... (truncated)[/dim]",
        title="[bold yellow]Context String sent to LLM[/bold yellow]",
        expand=True,
    ))


# ── Main (standalone test) ────────────────────────────────────────────────────
def main():
    console.rule("[bold cyan]RoadmapRAG — Retriever Test[/bold cyan]")

    retriever = Retriever()

    test_queries = [
        "I want to become a Data Scientist",
        "I want to learn web development with React",
        "I want to get into cybersecurity and ethical hacking",
    ]

    for query in test_queries:
        result = retriever.retrieve(query, top_k=3)
        _print_results(result)
        console.print("\n" + "─" * 80 + "\n")

    console.print("\n[bold green]✅ Retriever working correctly![/bold green]")
    console.print("Next  →  [bold cyan]python -m pipeline.generator[/bold cyan]\n")


if __name__ == "__main__":
    main()