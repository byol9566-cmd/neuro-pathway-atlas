#!/usr/bin/env python3
"""Axis of the vertebral canal from the BodyParts3D vertebrae -> data/derived/bp3d/canal_axis.json.

    pipeline/.venv/bin/python pipeline/bp3d_canal_axis.py

For each vertebra (C1..L5 and the sacrum) the canal is the hole between the body and the laminae: on the
vertebra's mid-level slice, within a narrow band about the midline, the largest gap in the y histogram
is the canal; its middle is the canal centre. The curve through these centres is what the Visible Human
cord is re-posed onto (vhp_derive.py) and what the modelled lumbar extension follows (models.cord_axis),
so the cord, its columns, the spinal tracts and the sympathetic trunk all sit inside the body's spine.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
from atlas_pipeline import bp3d  # noqa: E402

ORDINALS = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth"]
NAMES = [f"{o} cervical vertebra" for o in ORDINALS[:7]] + [f"{o} thoracic vertebra" for o in ORDINALS[:12]] + [f"{o} lumbar vertebra" for o in ORDINALS[:5]]
OUT = ROOT / "data" / "derived" / "bp3d" / "canal_axis.json"


def canal_centre(mesh):
    V = mesh.vertices
    zc = float(np.median(V[:, 2]))
    sl = V[np.abs(V[:, 2] - zc) < 4]
    if len(sl) < 30:
        sl = V
    xm = float(np.median(sl[:, 0]))
    band = sl[np.abs(sl[:, 0] - xm) < 7]
    ys = np.sort(band[:, 1])
    gaps = np.diff(ys)
    k = int(np.argmax(gaps))
    if gaps[k] < 6:  # no clear hole: fall back to a point behind the body
        return [xm, float(np.percentile(sl[:, 1], 35)), zc, 0.0]
    return [xm, float((ys[k] + ys[k + 1]) / 2), zc, float(gaps[k])]


def main():
    idx = bp3d.index()
    rows = []
    for n in NAMES:
        if n not in idx:
            print("missing", n); continue
        m = bp3d.mesh_for([n], max_faces=10**9)
        x, y, z, gap = canal_centre(m)
        rows.append({"vertebra": n, "x": round(x, 1), "y": round(y, 1), "z": round(z, 1), "gapMm": round(gap, 1)})
        print(f"{n:28s} canal ({x:6.1f}, {y:6.1f}, {z:7.1f})  gap {gap:.0f} mm")
    rows.sort(key=lambda r: -r["z"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"source": "BodyParts3D vertebrae, MNI (bp3d.to_mni)", "points": rows}, indent=1))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
