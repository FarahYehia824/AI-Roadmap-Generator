"""
retriever.py
────────────
User query  →  Embed  →  Search FAISS  →  Return ranked context
"""

import os
import pickle
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import faiss
from dotenv import load_dotenv
from loguru import logger
from sentence_transformers import SentenceTransformer

load_dotenv()

FAISS_DIR       = Path(os.getenv("FAISS_DIR", "./faiss_store"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
TOP_K           = int(os.getenv("TOP_K_RESULTS", 5))


# ── Data classes ──────────────────────────────────────────────────────────────
@dataclass
class RetrievedChunk:
    text      : str
    metadata  : dict
    score     : float
    chunk_type: str


@dataclass
class RetrievalResult:
    query         : str
    skills        : list = field(default_factory=list)
    roadmap_steps : list = field(default_factory=list)
    resources     : list = field(default_factory=list)

    def all_chunks(self):
        return self.skills + self.roadmap_steps + self.resources

    def as_context_string(self) -> str:
        parts = []
        if self.skills:
            parts.append("=== RELEVANT SKILLS ===")
            for c in self.skills:
                parts.append(c.text)
                parts.append("")
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


# ── FAISS store loader ────────────────────────────────────────────────────────
def load_store(name: str):
    index = faiss.read_index(str(FAISS_DIR / f"{name}.index"))
    with open(FAISS_DIR / f"{name}.pkl", "rb") as f:
        data = pickle.load(f)
    return index, data["texts"], data["metas"]


# ── Retriever ─────────────────────────────────────────────────────────────────
class Retriever:

    def __init__(self):
        logger.info("Initialising Retriever (FAISS) ...")
        self.model = SentenceTransformer(EMBEDDING_MODEL)

        self.idx_skills,    self.txt_skills,    self.meta_skills    = load_store("skills")
        self.idx_roadmaps,  self.txt_roadmaps,  self.meta_roadmaps  = load_store("roadmaps")
        self.idx_resources, self.txt_resources, self.meta_resources = load_store("resources")

        logger.success("FAISS stores loaded.")

    def _embed(self, text: str) -> np.ndarray:
        vec = self.model.encode([text]).astype("float32")
        faiss.normalize_L2(vec)
        return vec

    def _search(self, index, texts, metas, query_vec, top_k, chunk_type) -> list:
        k = min(top_k, index.ntotal)
        scores, indices = index.search(query_vec, k)
        chunks = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            chunks.append(RetrievedChunk(
                text=texts[idx],
                metadata=metas[idx],
                score=round(float(score), 4),
                chunk_type=chunk_type,
            ))
        return chunks

    def retrieve(self, query: str, top_k: int = TOP_K) -> RetrievalResult:
        logger.info(f'Retrieving: "{query}"')
        vec = self._embed(query)

        skill_chunks    = self._search(self.idx_skills,    self.txt_skills,    self.meta_skills,    vec, top_k, "skill")
        roadmap_chunks  = self._search(self.idx_roadmaps,  self.txt_roadmaps,  self.meta_roadmaps,  vec, top_k, "roadmap_step")
        resource_chunks = self._search(self.idx_resources, self.txt_resources, self.meta_resources, vec, top_k, "resource")

        logger.success(f"Retrieved {len(skill_chunks)} skills | {len(roadmap_chunks)} steps | {len(resource_chunks)} resources")

        return RetrievalResult(
            query=query,
            skills=skill_chunks,
            roadmap_steps=roadmap_chunks,
            resources=resource_chunks,
        )


# ── Standalone test ───────────────────────────────────────────────────────────
def main():
    retriever = Retriever()
    queries = [
        "I want to become a Data Scientist",
        "I want to learn web development with React",
        "I want to get into cybersecurity",
    ]
    for q in queries:
        result = retriever.retrieve(q, top_k=3)
        print(f"\n Query: {q}")
        print(f"  Skills:    {[c.metadata.get('name','?') for c in result.skills]}")
        print(f"  Roadmap:   {[c.metadata.get('track','?') for c in result.roadmap_steps]}")
        print(f"  Resources: {[c.metadata.get('skill_name','?') for c in result.resources]}")
    print("\n✅ Retriever working!")


if __name__ == "__main__":
    main()