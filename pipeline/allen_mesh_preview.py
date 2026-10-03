#!/usr/bin/env python3
"""Mesh the registered Allen label volume (deep structures) into one GLB for a visual check.
    pipeline/.venv/bin/python pipeline/allen_mesh_preview.py <scratch/allen>
Research/educational use only (Allen terms of use)."""
import json, sys
from pathlib import Path
import numpy as np, trimesh
sys.path.insert(0, str(Path(__file__).resolve().parent))
from atlas_pipeline import meshing

S = Path(sys.argv[1])
r = np.load(S / (sys.argv[2] if len(sys.argv) > 2 else "register_result.npz")); vol = r["vol"]; MM = float(r["mm"]); origin = r["origin"]
onto = {s["id"]: s for s in json.loads((S / "ontology16.json").read_text())}
stats = json.loads((S / "stack_stats.json").read_text())
ids, counts = np.unique(vol, return_counts=True)
# deep structures only: skip cortex gyri, white matter, ventricles, sulci; keep >= 15 mm3
skip_words = ("gyrus", "white matter", "ventricle", "sulcus", "lobule", "cortex", "area", "fissure", "capsule", "corpus callosum", "radiation")
keep = []
for i, c in zip(ids, counts):
    if i == 0: continue
    name = (onto.get(int(i)) or {}).get("name", "") or ""
    if any(w in name.lower() for w in skip_words): continue
    if c * MM**3 < 15: continue
    keep.append((int(i), name, c * MM**3))
print("meshing", len(keep), "structures")
scene = trimesh.Scene()
rng = np.random.default_rng(1)
records = []
for i, name, mm3 in sorted(keep, key=lambda t: -t[2]):
    mask = vol == i
    try:
        cleaned, stats_ = meshing.clean_mask(mask)
        mesh = meshing.mask_to_mesh(cleaned, MM, origin, smooth_sigma_mm=0.8)
        mesh = meshing.simplify(mesh, meshing.target_face_count(mesh, 3.0, hi=6000))
    except Exception as e:
        print("  skip", name, e); continue
    color = rng.integers(70, 240, 3)
    mesh.visual = trimesh.visual.ColorVisuals(mesh, face_colors=np.tile(np.append(color, 255), (len(mesh.faces), 1)))
    scene.add_geometry(mesh, node_name=f"a{i}", geom_name=f"a{i}")
    records.append({"id": i, "name": name, "mm3": round(mm3, 1), "faces": len(mesh.faces), "centroid": np.round(mesh.centroid, 1).tolist()})
(S / "preview_meshes.json").write_text(json.dumps(records, indent=1))
scene.export(S / (sys.argv[3] if len(sys.argv) > 3 else "allen_preview.glb"))
print("wrote", S / "allen_preview.glb", "meshes", len(records), "faces", sum(x["faces"] for x in records))
