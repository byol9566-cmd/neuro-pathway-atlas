#!/usr/bin/env python3
"""Build the next content/structures.json: our 53 + the reviewer's new structures that we can give 3D.

    pipeline/.venv/bin/python pipeline/integrate_structures.py [--write]

Inputs
  content/structures.json                                   our current 53 (kept verbatim)
  ~/Downloads/atlas-refs/seongyeon-2026-10-02/structures.json   the reviewer's 402 (names, groups)
  docs/data/structures-3d/label-mapping.json                NextBrain / AAN labels per new structure (agent, reviewed)
  docs/data/structures-3d/placeholders.json                 MNI centre + radii for structures no atlas covers (agent, reviewed)

Rules: only `confidence` high/medium mappings and placeholders are used; a new structure that the mapping
says is a duplicate of one of our 53 is dropped (the pathways will be re-pointed to the existing id);
everything else stays out of the 3D list and is reported. Without --write it only prints the summary.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OURS = ROOT / "content" / "structures.json"
THEIRS = Path.home() / "Downloads" / "atlas-refs" / "seongyeon-2026-10-02" / "structures.json"
MAPPING = ROOT / "docs" / "data" / "structures-3d" / "label-mapping.json"
PLACEHOLDERS = ROOT / "docs" / "data" / "structures-3d" / "placeholders.json"
ALIASES = ROOT / "docs" / "data" / "structures-3d" / "aliases.json"  # new id -> existing id (written here)

# the viewer draws tracts as lines through a centreline: keep that for the reviewer's `tracts` group
TRACT_GROUP = "tracts"
# low-confidence mappings the main session rejected (2026-10-03); the rest of the low ones are accepted as
# gyral approximations and flagged in the viewer
LOW_DENY = {
    "so-olfactory-bulb": "anterior olfactory nucleus is not the bulb -> placeholder instead",
    "pn-cn4": "root label has ~0 volume; a nerve is not placeable",
    "bs-cvlm": "whole medullary reticular formation would mislead -> placeholder",
    "bs-rvlm": "whole medullary reticular formation would mislead -> placeholder",
    "bs-gigantocellular": "whole medullary reticular formation would mislead -> placeholder",
    "bs-reticulotegmental": "whole pontine reticular formation would mislead -> placeholder",
}


def main(write: bool):
    ours = json.loads(OURS.read_text(encoding="utf-8"))
    theirs = json.loads(THEIRS.read_text(encoding="utf-8"))
    mapping = json.loads(MAPPING.read_text(encoding="utf-8"))
    placeholders = json.loads(PLACEHOLDERS.read_text(encoding="utf-8")) if PLACEHOLDERS.exists() else {"items": []}
    our_ids = {s["id"] for s in ours["structures"]}
    by_id = {s["id"]: s for s in theirs["structures"]}

    aliases = {a["id"]: a["existingId"] for a in mapping.get("alreadyUsedBy", []) if a.get("existingId") in our_ids}
    new, skipped = [], []
    # label sets of our existing NextBrain structures: a new structure with the SAME labels is the same
    # thing under another name (alias), one with a SUBSET is a subpart we can still draw on its own
    existing_labels = {}
    for s in ours["structures"]:
        src = s["source"]
        if src.get("atlas") == "nextbrain" and isinstance(src.get("labels"), list):
            labels = set(src["labels"])
            for lo, hi in src.get("labelRanges", []):
                labels |= set(range(lo, hi + 1))
            existing_labels[s["id"]] = labels
    subparts = {}
    for sub in ("bs-solitary-rostral", "bs-solitary-caudal"):
        aliases.setdefault(sub, "bs-solitary")
    for m in mapping.get("mapped", []):
        if m["atlas"] != "nextbrain" or m["id"] in our_ids:
            continue
        mine = set(m["labels"])
        for eid, theirs_labels in existing_labels.items():
            if mine == theirs_labels:
                aliases.setdefault(m["id"], eid)
                break
            if mine < theirs_labels:
                subparts[m["id"]] = eid

    for m in mapping.get("mapped", []):
        sid = m["id"]
        if sid in our_ids or sid in aliases or sid not in by_id:
            continue
        if not m.get("labels") or sid in LOW_DENY:
            skipped.append((sid, "no labels" if not m.get("labels") else f"low-confidence mapping rejected: {LOW_DENY[sid]}"))
            continue
        base = by_id[sid]
        entry = {"id": sid, "group": base["group"], "name": base["name"]}
        if m["atlas"] == "nextbrain":
            entry["source"] = {"atlas": "nextbrain", "labels": m["labels"]}
            if base["group"] == TRACT_GROUP:
                entry["tract"] = True
        elif m["atlas"] == "aan":
            # the combined v2.0 volume holds LC/LDTg/mRt/PBC/PnO/PTg only as left/right labels (73xx/74xx);
            # their bilateral ids 7205-7210 are empty there, so translate them
            split = {7205: (7301, 7401), 7206: (7302, 7402), 7207: (7303, 7403), 7208: (7304, 7404), 7209: (7305, 7405), 7210: (7306, 7406)}
            labels = []
            for l in m["labels"]:
                labels += list(split[l]) if l in split else [l]
            # bilateral-in-one-label nuclei get side M; L/R split ids come in pairs
            if len(labels) == 1:
                entry["source"] = {"atlas": "aan", "labels": {"M": labels}}
            else:
                left = [l for l in labels if 7300 <= l < 7400]
                right = [l for l in labels if 7400 <= l < 7500]
                entry["source"] = {"atlas": "aan", "labels": {"L": left, "R": right}} if left and right else {"atlas": "aan", "labels": {"M": labels}}
        else:
            skipped.append((sid, f"unknown atlas {m['atlas']}"))
            continue
        if m.get("approx"):
            entry["approxArea"] = True
        if sid in subparts:
            entry["subpartOf"] = subparts[sid]
        entry["mapping"] = {"confidence": m.get("confidence"), "labelNames": m.get("labelNames"), "note": m.get("note", "")}
        new.append(entry)

    mapped_ids = {e["id"] for e in new}
    for it in placeholders.get("items", []):
        sid = it["id"]
        if not it.get("placeable") or sid in our_ids or sid in mapped_ids or sid in aliases or sid not in by_id:
            continue
        # the owner's rule: build it whenever position and size can be stated, whatever the shape — so low
        # confidence placeholders go in too, flagged as approximate for the viewer
        base = by_id[sid]
        new.append({"id": sid, "group": base["group"], "name": base["name"],
                    "source": {"atlas": "mni", "centreMni": it["centreMni"], "radiiMm": it["radiiMm"], "bilateral": bool(it.get("bilateral"))},
                    "placeholderNote": {"source": it.get("source"), "confidence": it.get("confidence"), "note": it.get("note", "")}})

    out = {**ours, "groups": {**theirs["groups"], **ours.get("groups", {})}, "structures": ours["structures"] + new}
    print(f"ours {len(ours['structures'])} + new {len(new)} = {len(out['structures'])} | aliases {len(aliases)} | skipped {len(skipped)}")
    from collections import Counter
    print(" new by group:", dict(Counter(e["group"] for e in new)))
    print(" new by source:", dict(Counter(e["source"]["atlas"] for e in new)))
    for sid, why in skipped[:15]:
        print("  skip", sid, why)
    if write:
        OURS.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        ALIASES.write_text(json.dumps(aliases, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("written", OURS, "and", ALIASES)


if __name__ == "__main__":
    main("--write" in sys.argv)
