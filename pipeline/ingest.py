"""
ingest.py
─────────
Load JSON data  →  Build rich text chunks  →  Embed  →  Store in ChromaDB

Run:
    python -m pipeline.ingest
"""

import json
import os
from pathlib import Path

import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from sentence_transformers import SentenceTransformer

load_dotenv()
console = Console()

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR           = Path("data")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
EMBEDDING_MODEL    = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

COLLECTION_SKILLS    = "skills"
COLLECTION_ROADMAPS  = "roadmaps"
COLLECTION_RESOURCES = "resources"


# ── Loaders ───────────────────────────────────────────────────────────────────
def load_json(filename: str) -> list[dict]:
    path = DATA_DIR / filename
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════════════════════════
# CHUNKERS
# Each function converts one JSON record → rich plain-text chunk.
# Rich descriptive text → better embeddings → better retrieval.
# ══════════════════════════════════════════════════════════════════════════════

def chunk_skill(skill: dict) -> str:
    """
    Example output:
        SKILL: Python Programming
        Category: Programming | Level: Beginner
        Tracks: Data Science & ML, Backend, Cybersecurity
        Description: Core Python syntax, data types, loops ...
        Prerequisites: None
        Estimated Hours: 40
        Tags: python, programming, coding, scripting
    """
    prereqs = ", ".join(skill.get("prerequisites", [])) or "None"
    tags    = ", ".join(skill.get("tags", []))
    tracks  = ", ".join(skill.get("tracks", []))

    return (
        f"SKILL: {skill['name']}\n"
        f"Category: {skill['category']} | Level: {skill['level']}\n"
        f"Tracks: {tracks}\n"
        f"Description: {skill['description']}\n"
        f"Prerequisites: {prereqs}\n"
        f"Estimated Hours: {skill.get('estimated_hours', 'N/A')}\n"
        f"Tags: {tags}"
    )


def chunk_roadmap_step(step: dict, roadmap: dict) -> str:
    """
    Example output:
        ROADMAP STEP: Data Science & ML — Step 1
        Goal: Become a Data Scientist / ML Engineer
        Title: Learn Python Programming
        Level: Beginner | Duration: 4 weeks
        Why: Python is the primary language for data science ...
        Milestone: Build a small automation script or data parser
        Skill ID: sk_001
    """
    return (
        f"ROADMAP STEP: {roadmap['track']} — Step {step['order']}\n"
        f"Goal: {roadmap['goal']}\n"
        f"Title: {step['title']}\n"
        f"Level: {step['level']} | Duration: {step['duration_weeks']} weeks\n"
        f"Why: {step['why']}\n"
        f"Milestone: {step.get('milestone', 'N/A')}\n"
        f"Skill ID: {step['skill_id']}"
    )


def chunk_resource(resource: dict, skill_name: str) -> str:
    """
    Example output:
        RESOURCE for Python Programming:
        Title: Python for Everybody Specialization
        Platform: Coursera | Type: course | Level: Beginner
        Free: No (audit available)
        Duration: 32 hours
        Why Recommended: Best structured beginner Python course ...
        Link: https://...
    """
    if resource.get("free"):
        free_text = "Yes (free)"
    elif resource.get("audit_available"):
        free_text = "No (audit available)"
    else:
        free_text = "No (paid)"

    return (
        f"RESOURCE for {skill_name}:\n"
        f"Title: {resource['title']}\n"
        f"Platform: {resource['platform']} | Type: {resource['type']} | Level: {resource['level']}\n"
        f"Free: {free_text}\n"
        f"Duration: {resource.get('duration_hours', 'N/A')} hours\n"
        f"Why Recommended: {resource.get('why_recommended', 'N/A')}\n"
        f"Link: {resource.get('link', 'N/A')}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# CHUNK BUILDERS  →  return (texts, metadatas, ids)
# Metadata is stored alongside vectors — lets us filter results later.
# ══════════════════════════════════════════════════════════════════════════════

def build_skill_chunks(skills):
    texts, metas, ids = [], [], []
    for skill in skills:
        texts.append(chunk_skill(skill))
        metas.append({
            "skill_id" : skill["id"],
            "name"     : skill["name"],
            "level"    : skill["level"],
            "category" : skill["category"],
            "tracks"   : ", ".join(skill.get("tracks", [])),
            "type"     : "skill",
        })
        ids.append(f"skill_{skill['id']}")
    return texts, metas, ids


def build_roadmap_chunks(roadmaps):
    texts, metas, ids = [], [], []
    for rm in roadmaps:
        for step in rm["steps"]:
            texts.append(chunk_roadmap_step(step, rm))
            metas.append({
                "track"          : rm["track"],
                "goal"           : rm["goal"],
                "step_order"     : str(step["order"]),   # chroma needs str/int/float/bool
                "skill_id"       : step["skill_id"],
                "level"          : step["level"],
                "duration_weeks" : str(step["duration_weeks"]),
                "type"           : "roadmap_step",
            })
            ids.append(f"roadmap_{rm['id']}_step{step['order']}")
    return texts, metas, ids


def build_resource_chunks(resources):
    texts, metas, ids = [], [], []
    for bundle in resources:
        for i, res in enumerate(bundle["resources"]):
            texts.append(chunk_resource(res, bundle["skill_name"]))
            metas.append({
                "skill_id"        : bundle["skill_id"],
                "skill_name"      : bundle["skill_name"],
                "platform"        : res["platform"],
                "level"           : res["level"],
                "free"            : str(res.get("free", False)),
                "audit_available" : str(res.get("audit_available", False)),
                "type"            : "resource",
            })
            ids.append(f"resource_{bundle['skill_id']}_{i}")
    return texts, metas, ids


# ══════════════════════════════════════════════════════════════════════════════
# EMBED + STORE
# ══════════════════════════════════════════════════════════════════════════════

def embed_and_store(collection, model, texts, metadatas, ids, label):
    """
    1. Encode all texts → list of vectors  (done in one fast batch)
    2. Upsert into ChromaDB collection     (safe to re-run)
    """
    logger.info(f"Embedding {len(texts)} {label} chunks ...")

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        
    ).tolist()

    # upsert = insert OR update if ID exists → idempotent
    collection.upsert(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )
    logger.success(f"  ✓ {len(texts)} {label} chunks stored in ChromaDB.")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    console.rule("[bold cyan]RoadmapRAG — Ingest Pipeline[/bold cyan]")

    # ── Step 1: Load ──────────────────────────────────────────────────────────
    console.print("\n[bold]Step 1/4[/bold]  Loading JSON data ...")
    skills    = load_json("skills.json")
    roadmaps  = load_json("roadmaps.json")
    resources = load_json("resources.json")
    total_steps     = sum(len(r["steps"]) for r in roadmaps)
    total_resources = sum(len(b["resources"]) for b in resources)
    console.print(
        f"         ✓ {len(skills)} skills | "
        f"{total_steps} roadmap steps | "
        f"{total_resources} resources"
    )

    # ── Step 2: Chunking ──────────────────────────────────────────────────────
    console.print("\n[bold]Step 2/4[/bold]  Building text chunks ...")
    s_texts, s_metas, s_ids = build_skill_chunks(skills)
    r_texts, r_metas, r_ids = build_roadmap_chunks(roadmaps)
    c_texts, c_metas, c_ids = build_resource_chunks(resources)
    total = len(s_texts) + len(r_texts) + len(c_texts)
    console.print(
        f"         ✓ {len(s_texts)} skill chunks | "
        f"{len(r_texts)} roadmap chunks | "
        f"{len(c_texts)} resource chunks  "
        f"([bold green]{total} total[/bold green])"
    )

    # ── Preview one chunk of each type ────────────────────────────────────────
    console.print("\n[dim]── Sample chunk (skill) ──────────────────────────────[/dim]")
    console.print(f"[dim]{s_texts[0]}[/dim]")
    console.print("\n[dim]── Sample chunk (roadmap step) ──────────────────────[/dim]")
    console.print(f"[dim]{r_texts[0]}[/dim]")
    console.print("\n[dim]── Sample chunk (resource) ───────────────────────────[/dim]")
    console.print(f"[dim]{c_texts[0]}[/dim]\n")

    # ── Step 3: Load model ────────────────────────────────────────────────────
    console.print(f"[bold]Step 3/4[/bold]  Loading embedding model [cyan]{EMBEDDING_MODEL}[/cyan] ...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    console.print("         ✓ Model ready.")

    # ── Step 4: Embed + Store ─────────────────────────────────────────────────
    console.print(f"\n[bold]Step 4/4[/bold]  Embedding + storing → [cyan]{CHROMA_PERSIST_DIR}[/cyan]")
    client = chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False),
    )

    # Drop old data so re-runs stay clean
    for name in [COLLECTION_SKILLS, COLLECTION_ROADMAPS, COLLECTION_RESOURCES]:
        try:
            client.delete_collection(name)
            logger.debug(f"Dropped old collection: {name}")
        except Exception:
            pass

    col_skills    = client.create_collection(COLLECTION_SKILLS,    metadata={"hnsw:space": "cosine"})
    col_roadmaps  = client.create_collection(COLLECTION_ROADMAPS,  metadata={"hnsw:space": "cosine"})
    col_resources = client.create_collection(COLLECTION_RESOURCES, metadata={"hnsw:space": "cosine"})

    embed_and_store(col_skills,    model, s_texts, s_metas, s_ids, "skill")
    embed_and_store(col_roadmaps,  model, r_texts, r_metas, r_ids, "roadmap")
    embed_and_store(col_resources, model, c_texts, c_metas, c_ids, "resource")

    # ── Summary ───────────────────────────────────────────────────────────────
    console.rule("[bold green]✅  Ingest Complete[/bold green]")
    console.print(
        f"\n  Vector store: [cyan]{CHROMA_PERSIST_DIR}[/cyan]\n"
        f"\n  Collections:"
        f"\n    [bold]skills[/bold]     →  {col_skills.count()} vectors"
        f"\n    [bold]roadmaps[/bold]   →  {col_roadmaps.count()} vectors"
        f"\n    [bold]resources[/bold]  →  {col_resources.count()} vectors"
        f"\n\n  Next  →  [bold cyan]python -m pipeline.retriever[/bold cyan]\n"
    )


if __name__ == "__main__":
    main()