"""Basic sanity tests for data integrity."""
import json, pathlib

DATA = pathlib.Path("data")

def load(name):
    return json.loads((DATA / name).read_text())

def test_skills_not_empty():
    assert len(load("skills.json")) > 0

def test_roadmaps_not_empty():
    assert len(load("roadmaps.json")) > 0

def test_skill_ids_unique():
    ids = [s["id"] for s in load("skills.json")]
    assert len(ids) == len(set(ids))

def test_roadmap_skill_refs_valid():
    skill_ids = {s["id"] for s in load("skills.json")}
    for rm in load("roadmaps.json"):
        for step in rm["steps"]:
            assert step["skill_id"] in skill_ids, \
                f"Broken ref: {step['skill_id']} in {rm['track']}"

def test_resources_skill_refs_valid():
    skill_ids = {s["id"] for s in load("skills.json")}
    for r in load("resources.json"):
        assert r["skill_id"] in skill_ids, \
            f"Broken ref: {r['skill_id']} in resources"
