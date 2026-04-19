"""
ingest.py
─────────
Load JSON data  →  Build rich text chunks  →  Embed  →  Store in FAISS

Run:
    python -m pipeline.ingest
"""

import json
import os
import pickle
from pathlib import Path

import numpy as np
import faiss
from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from sentence_transformers import SentenceTransformer

load_dotenv()
console = Console()

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR        = Path("data")
FAISS_DIR       = Path(os.getenv("FAISS_DIR", "./faiss_store"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


# ── Loaders ───────────────────────────────────────────────────────────────────
def load_json(filename: str) -> list[dict]:
    path = DATA_DIR / filename
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Chunkers ──────────────────────────────────────────────────────────────────
def chunk_skill(skill: dict) -> str:
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


# ── Chunk builders ────────────────────────────────────────────────────────────
def build_skill_chunks(skills):
    texts, metas = [], []
    for skill in skills:
        texts.append(chunk_skill(skill))
        metas.append({
            "skill_id": skill["id"],
            "name"    : skill["name"],
            "level"   : skill["level"],
            "category": skill["category"],
            "tracks"  : ", ".join(skill.get("tracks", [])),
            "type"    : "skill",
        })
    return texts, metas


def build_roadmap_chunks(roadmaps):
    texts, metas = [], []
    for rm in roadmaps:
        for step in rm["steps"]:
            texts.append(chunk_roadmap_step(step, rm))
            metas.append({
                "track"         : rm["track"],
                "goal"          : rm["goal"],
                "step_order"    : str(step["order"]),
                "skill_id"      : step["skill_id"],
                "level"         : step["level"],
                "duration_weeks": str(step["duration_weeks"]),
                "type"          : "roadmap_step",
            })
    return texts, metas


def build_resource_chunks(resources):
    texts, metas = [], []
    for bundle in resources:
        for res in bundle["resources"]:
            texts.append(chunk_resource(res, bundle["skill_name"]))
            metas.append({
                "skill_id"       : bundle["skill_id"],
                "skill_name"     : bundle["skill_name"],
                "platform"       : res["platform"],
                "level"          : res["level"],
                "free"           : str(res.get("free", False)),
                "audit_available": str(res.get("audit_available", False)),
                "type"           : "resource",
            })
    return texts, metas


# ── FAISS store ───────────────────────────────────────────────────────────────
def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    """Build a cosine-similarity FAISS index."""
    dim   = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)        # Inner Product = cosine after normalizing
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    return index


def save_store(name: str, index: faiss.Index, texts: list, metas: list):
    FAISS_DIR.mkdir(exist_ok=True)
    faiss.write_index(index, str(FAISS_DIR / f"{name}.index"))
    with open(FAISS_DIR / f"{name}.pkl", "wb") as f:
        pickle.dump({"texts": texts, "metas": metas}, f)
    logger.success(f"  ✓ {len(texts)} chunks saved → {name}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    console.rule("[bold cyan]RoadmapRAG — Ingest Pipeline (FAISS)[/bold cyan]")

    # Step 1: Load
    console.print("\n[bold]Step 1/4[/bold]  Loading JSON data ...")
    skills    = load_json("skills.json")
    roadmaps  = load_json("roadmaps.json")
    resources = load_json("resources.json")
    console.print(f"         ✓ {len(skills)} skills | "
                  f"{sum(len(r['steps']) for r in roadmaps)} steps | "
                  f"{sum(len(b['resources']) for b in resources)} resources")

    # Step 2: Chunk
    console.print("\n[bold]Step 2/4[/bold]  Building text chunks ...")
    s_texts, s_metas = build_skill_chunks(skills)
    r_texts, r_metas = build_roadmap_chunks(roadmaps)
    c_texts, c_metas = build_resource_chunks(resources)
    total = len(s_texts) + len(r_texts) + len(c_texts)
    console.print(f"         ✓ {len(s_texts)} skill | {len(r_texts)} roadmap | "
                  f"{len(c_texts)} resource  ([bold green]{total} total[/bold green])")

    # Step 3: Embed
    console.print(f"\n[bold]Step 3/4[/bold]  Loading model [cyan]{EMBEDDING_MODEL}[/cyan] ...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    console.print("         ✓ Model ready.")

    all_texts = s_texts + r_texts + c_texts
    console.print(f"\n[bold]Step 4/4[/bold]  Embedding {total} chunks ...")
    all_embeddings = model.encode(all_texts, batch_size=32,
                                  show_progress_bar=False).astype("float32")

    s_emb = all_embeddings[:len(s_texts)]
    r_emb = all_embeddings[len(s_texts):len(s_texts)+len(r_texts)]
    c_emb = all_embeddings[len(s_texts)+len(r_texts):]

    # Step 4: Save
    save_store("skills",    build_faiss_index(s_emb.copy()), s_texts, s_metas)
    save_store("roadmaps",  build_faiss_index(r_emb.copy()), r_texts, r_metas)
    save_store("resources", build_faiss_index(c_emb.copy()), c_texts, c_metas)

    console.rule("[bold green]✅  Ingest Complete[/bold green]")
    console.print(f"\n  FAISS store → [cyan]{FAISS_DIR}[/cyan]")
    console.print(f"  skills: {len(s_texts)} | roadmaps: {len(r_texts)} | resources: {len(c_texts)}\n")


if __name__ == "__main__":
    main()