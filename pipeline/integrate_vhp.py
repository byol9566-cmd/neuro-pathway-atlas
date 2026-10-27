#!/usr/bin/env python3
"""Register Visible-Human-segmented structures in content/structures.json, replacing their MNI placeholders.

    pipeline/.venv/bin/python pipeline/integrate_vhp.py [--write]

For every data/derived/vhp/<id>.<side>.mni.nii.gz: if <id> exists with source.atlas == "mni", the entry is
switched to {"atlas": "vhp", "file": ..., "side": ...}; bilateral structures get one entry per side
(the viewer expects <id>.L and <id>.R meshes). Attribution: Visible Human Project, U.S. National Library of
Medicine (no licence required).
"""
import sys
from pathlib import Path

from atlas_pipeline.content import STRUCTURES as CONTENT, load_structures, save_structures, structure_index

ROOT = Path(__file__).resolve().parent.parent
DER = ROOT / "data" / "derived" / "vhp"


def main(write):
    data = load_structures()
    by_id = structure_index(data)
    files = sorted(DER.glob("*.mni.nii.gz"))
    changed = []
    for f in files:
        sid, side = f.name.replace(".mni.nii.gz", "").rsplit(".", 1)
        s = by_id.get(sid)
        if not s:
            print("no structure for", f.name); continue
        src = s["source"]
        if src.get("atlas") == "vhp":
            src.setdefault("files", {})[side] = str(f.relative_to(ROOT))
        else:
            s["source"] = {"atlas": "vhp", "files": {side: str(f.relative_to(ROOT))}, "replaced": src}
        changed.append((sid, side))
    # the build reads one file per entry; expand bilateral entries into per-side file lists the build can walk
    for s in data["structures"]:
        src = s["source"]
        if src.get("atlas") == "vhp" and "files" in src:
            sides = src["files"]
            src["file"] = next(iter(sides.values()))
            src["side"] = next(iter(sides.keys()))
            src["sides"] = sides
    print("vhp structures:", changed)
    if write:
        save_structures(data)
        print("written", CONTENT)


if __name__ == "__main__":
    main("--write" in sys.argv)
