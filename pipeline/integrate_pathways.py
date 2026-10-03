#!/usr/bin/env python3
"""Build content/pathways.json from the reviewer's dataset (2026-10-02) for the viewer.

    pipeline/.venv/bin/python pipeline/integrate_pathways.py [--write]

What changes between their file and ours
  * `structures` of a step = their `structures` + their `structureRefs`, with alias ids replaced
    (docs/data/structures-3d/aliases.json) and only ids that exist in content/structures.json kept.
    So every structure we now have a mesh for lights up, not only the original 53.
  * `missing.ko` lists, by Korean name, the participating structures we still have no 3D for.
  * `has3d` marks pathways with at least one drawable step; the viewer lists the others separately.
  * `categories` block gives Korean names and a display order for the 20 categories.
  * Extension fields the viewer does not read (edges, sourceRefs, topology, molecules ...) are dropped
    from the app file; the full dataset stays under ~/Downloads/atlas-refs/.
Their corrected versions of dcml / papez / hvor replace ours (same ids, same step ids).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEIRS = Path.home() / "Downloads" / "atlas-refs" / "seongyeon-2026-10-02"
OUT = ROOT / "content" / "pathways.json"

CATEGORIES = [  # display order
    ("somatosensory", "체성감각"), ("pain", "통증"), ("motor", "운동"), ("basal-ganglia", "바닥핵"), ("cerebellar", "소뇌"),
    ("reflex", "반사"), ("oculomotor", "눈운동"), ("visual", "시각"), ("auditory", "청각"), ("vestibular", "안뜰"),
    ("gustatory", "미각"), ("olfactory", "후각"), ("limbic", "둘레계통·기억"), ("learning", "학습·가소성"), ("arousal", "각성·수면"),
    ("autonomic", "자율신경"), ("neuroendocrine", "신경내분비"), ("cognition", "인지"), ("language", "언어"), ("cellular", "세포·시냅스 기전"),
]


def main(write: bool):
    theirs_p = json.loads((THEIRS / "pathways.json").read_text(encoding="utf-8"))
    theirs_s = json.loads((THEIRS / "structures.json").read_text(encoding="utf-8"))
    ours_s = json.loads((ROOT / "content" / "structures.json").read_text(encoding="utf-8"))
    aliases = json.loads((ROOT / "docs" / "data" / "structures-3d" / "aliases.json").read_text(encoding="utf-8"))
    have = {s["id"] for s in ours_s["structures"]}
    names = {s["id"]: s["name"]["ko"] for s in theirs_s["structures"]}

    out_paths, stats = [], {"steps": 0, "steps3d": 0, "paths3d": 0}
    for p in theirs_p["pathways"]:
        steps = []
        any3d = False
        for st in p["steps"]:
            seen, refs, missing = set(), [], []
            for r in list(st.get("structures", [])) + list(st.get("structureRefs", [])):
                sid = aliases.get(r["id"], r["id"])
                if sid in seen:
                    continue
                seen.add(sid)
                if sid in have:
                    refs.append({"id": sid, "side": r.get("side", "ipsi")})
                else:
                    missing.append(names.get(r["id"], r["id"]))
            step = {"id": st["id"], "title": st["title"], "description": st["description"], "structures": refs}
            if st.get("neuronOrder"):
                step["neuronOrder"] = st["neuronOrder"]
            if st.get("decussation"):
                step["decussation"] = True
            if st.get("transmitter"):
                step["transmitter"] = st["transmitter"]
            note = (st.get("missing") or {}).get("ko", "")
            if missing:
                note = (note + " · " if note else "") + "3D 없음: " + ", ".join(missing)
            if note:
                step["missing"] = {"ko": note}
            steps.append(step)
            stats["steps"] += 1
            if refs:
                stats["steps3d"] += 1
                any3d = True
        if any3d:
            stats["paths3d"] += 1
        out_paths.append({
            "id": p["id"], "category": p["category"], "name": p["name"], "summary": p["summary"], "origin": p["origin"],
            "defaultOriginSide": p.get("defaultOriginSide", "R"), "reviewStatus": p.get("reviewStatus", "draft"),
            "evidenceStatus": p.get("evidenceStatus"), "processType": p.get("processType"), "has3d": any3d,
            "steps": steps,
            "lesions": [{"level": l["level"], "deficit": l["deficit"], **({"side": l["side"]} if l.get("side") else {})} for l in p.get("lesions", [])],
        })

    order = {c: i for i, (c, _) in enumerate(CATEGORIES)}
    out_paths.sort(key=lambda p: (order.get(p["category"], 99), not p["has3d"], p["name"]["ko"]))
    out = {
        "_comment": "성연 데이터셋(2026-10-02, 강의 정리본 기반·초안)을 뷰어 형식으로 변환. 생성: pipeline/integrate_pathways.py. 설명 문장은 공개 문헌 근거로 다시 쓸 예정(docs/data/pathway-evidence/).",
        "categories": [{"id": c, "name": {"ko": ko}} for c, ko in CATEGORIES],
        "pathways": out_paths,
    }
    print(f"pathways {len(out_paths)} (3D {stats['paths3d']}) | steps {stats['steps']} (3D {stats['steps3d']})")
    if write:
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("written", OUT)


if __name__ == "__main__":
    main("--write" in sys.argv)
