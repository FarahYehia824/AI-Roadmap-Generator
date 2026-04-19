import json

def load(path):
    with open(path) as f:
        return json.load(f)

skills     = load("data/skills.json")
roadmaps   = load("data/roadmaps.json")
resources  = load("data/resources.json")

skill_ids = {s["id"] for s in skills}

print("=" * 55)
print("📦  DATA VALIDATION REPORT")
print("=" * 55)

# ── Skills ────────────────────────────────────────────────
print(f"\n✅  Skills       : {len(skills)} records")
tracks_covered = set()
for s in skills:
    for t in s["tracks"]:
        tracks_covered.add(t)
print(f"    Tracks covered: {sorted(tracks_covered)}")

# ── Roadmaps ──────────────────────────────────────────────
print(f"\n✅  Roadmaps     : {len(roadmaps)} tracks")
broken_links = []
for rm in roadmaps:
    total_steps = len(rm["steps"])
    total_weeks = rm["total_duration_weeks"]
    for step in rm["steps"]:
        if step["skill_id"] not in skill_ids:
            broken_links.append((rm["track"], step["skill_id"]))
    print(f"    [{rm['track']}]  {total_steps} steps  |  {total_weeks} weeks")

if broken_links:
    print(f"\n❌  Broken skill_id references in roadmaps:")
    for track, sid in broken_links:
        print(f"    {track} → {sid}")
else:
    print("\n    All skill_id references in roadmaps are valid ✓")

# ── Resources ─────────────────────────────────────────────
print(f"\n✅  Resources    : {len(resources)} skill bundles")
broken_res = []
total_res  = 0
for r in resources:
    if r["skill_id"] not in skill_ids:
        broken_res.append(r["skill_id"])
    total_res += len(r["resources"])

print(f"    Total courses : {total_res}")
if broken_res:
    print(f"❌  Broken skill_id references in resources: {broken_res}")
else:
    print("    All skill_id references in resources are valid ✓")

# ── Skills without resources ──────────────────────────────
res_covered = {r["skill_id"] for r in resources}
no_res = [s["id"] for s in skills if s["id"] not in res_covered]
if no_res:
    names = [s["name"] for s in skills if s["id"] in no_res]
    print(f"\n⚠️   Skills with no resources yet ({len(no_res)}):")
    for n in names:
        print(f"     - {n}")

print("\n" + "=" * 55)
print("🎯  Summary")
print("=" * 55)
print(f"  Skills    : {len(skills)}")
print(f"  Roadmaps  : {len(roadmaps)}")
print(f"  Courses   : {total_res}")
print(f"  Tracks    : {len(roadmaps)}")
print("  Status    :", "✅ All good!" if not broken_links and not broken_res else "❌ Fix broken references")
