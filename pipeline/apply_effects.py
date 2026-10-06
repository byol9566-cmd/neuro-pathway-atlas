#!/usr/bin/env python3
"""Body effects of pathway steps: which limb joint flexes (+deg) or extends (-deg) when the step is
reached (viewer: AtlasScene.setJointAngles). Schematic — the amounts are illustrative.

    pipeline/.venv/bin/python pipeline/apply_effects.py [--write]
"""
import json
import sys
from pathlib import Path

PATHWAYS = Path(__file__).resolve().parent.parent / "content" / "pathways.json"
EFFECTS = {
    "corticospinal-lateral-4": [{"joint": "elbow", "side": "contra", "angle": 70}],
    "corticospinal-anterior-4": [{"joint": "shoulder", "side": "ipsi", "angle": 25}],
    "rubrospinal-3": [{"joint": "elbow", "side": "contra", "angle": 50}],
    "reticulospinal-medullary-3": [{"joint": "elbow", "side": "ipsi", "angle": 30}],
    "reticulospinal-pontine-3": [{"joint": "knee", "side": "ipsi", "angle": -8}, {"joint": "hip", "side": "ipsi", "angle": -8}],
    "vestibulospinal-lateral-3": [{"joint": "knee", "side": "ipsi", "angle": -8}, {"joint": "ankle", "side": "ipsi", "angle": -15}],
    "withdrawal-reflex-3": [{"joint": "hip", "side": "ipsi", "angle": 40}, {"joint": "knee", "side": "ipsi", "angle": 60}],
    "stretch-reflex-3": [{"joint": "knee", "side": "ipsi", "angle": -20}],
    "tectospinal-3": [],
}


def main(write):
    p = json.loads(PATHWAYS.read_text(encoding="utf-8"))
    n = 0
    for pw in p["pathways"]:
        for st in pw["steps"]:
            if st["id"] in EFFECTS:
                if EFFECTS[st["id"]]:
                    st["effects"] = EFFECTS[st["id"]]; n += 1
                else:
                    st.pop("effects", None)
    print(f"{n} steps with effects")
    if write:
        PATHWAYS.write_text(json.dumps(p, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("written")


if __name__ == "__main__":
    main("--write" in sys.argv)
