"""BodyParts3D (DBCLS, CC BY 4.0) whole-body meshes brought into MNI space.

Data: data/raw/bodyparts3d/obj/isa_BP3D_4.0_obj_99/<FJ id>.obj (polygon-reduced 99 %), index
isa_element_parts.txt (FMA concept id, English name, element file id). Units are mm in a body frame with
x to the subject's left, y posterior, z up (DICOM-like LPS, z up). to_mni.json holds the similarity
(scale 0.96, pitch -7 deg) fitted on four landmarks — brain centroid and top from the 'segment of brain'
meshes, both eyeballs — against NextBrain / Visible Human positions; residuals 3-5 mm.

Attribution required by the licence: "BodyParts3D, © The Database Center for Life Science licensed under
CC Attribution 4.0 International".
"""
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import trimesh

from . import DATA_DIR, meshing

ROOT = DATA_DIR / "bodyparts3d"
OBJ = ROOT / "obj" / "isa_BP3D_4.0_obj_99"


@lru_cache(maxsize=1)
def index() -> dict[str, list[str]]:
    """English part name -> element file ids"""
    # leaf parts (isa) first; compound organs ('heart', 'skull', 'right lung') come from the part-of list as
    # the set of element files that make them up
    lists = []
    for fname in ("isa_element_parts.txt", "partof_element_parts.txt"):
        d: dict[str, set[str]] = {}
        for line in (ROOT / fname).read_text(errors="ignore").splitlines()[1:]:
            cid, name, fid = line.rstrip("\n").split("\t")
            d.setdefault(name, set()).add(fid)
        lists.append(d)
    isa, partof = lists
    out = {k: sorted(v) for k, v in isa.items()}
    for k, v in partof.items():
        out.setdefault(k, sorted(v))
    return out


@lru_cache(maxsize=1)
def transform():
    t = json.loads((ROOT / "to_mni.json").read_text())
    return float(t["scale"]), np.array(t["rotation"]), np.array(t["translation"])


def to_mni(v: np.ndarray) -> np.ndarray:
    s, R, t = transform()
    ras = v * np.array([-1.0, -1.0, 1.0])
    return s * (R @ ras.T).T + t


def load_part(fid: str) -> trimesh.Trimesh:
    m = trimesh.load(OBJ / f"{fid}.obj", force="mesh", process=False)
    return trimesh.Trimesh(to_mni(np.asarray(m.vertices, float)), np.asarray(m.faces).copy(), process=False)


def mesh_for(names: list[str], max_faces: int = 6000) -> trimesh.Trimesh:
    """union of the named parts (every element file of each name), simplified to a face budget"""
    idx = index()
    parts = []
    for n in names:
        if n not in idx:
            raise ValueError(f"BodyParts3D has no part named {n!r}")
        absent = [f for f in idx[n] if not (OBJ / f"{f}.obj").exists()]
        if absent:  # the part is still built, but without these pieces
            print(f"  bp3d: {n!r}: no .obj for element(s) {', '.join(absent)} in {OBJ}, left out", file=sys.stderr)
        parts += [load_part(f) for f in idx[n] if f not in absent]
    if not parts:
        raise ValueError(f"no mesh files for {names}")
    m = trimesh.util.concatenate(parts)
    m = trimesh.Trimesh(m.vertices, m.faces, process=True)  # merge duplicate vertices
    if len(m.faces) > max_faces:
        # no Taubin pass: the union of an organ's parts has internal walls and open edges, and smoothing
        # them throws spikes (the heart grew icicles)
        m = meshing.simplify(m, max_faces, taubin_iters=0)
    m.fix_normals()
    return m


def split_skin(skin: trimesh.Trimesh, limb: dict[str, trimesh.Trimesh], torso: list[trimesh.Trimesh]) -> dict[str, trimesh.Trimesh]:
    """Cut the skin into limb pieces so the limbs can move: every skin vertex goes to the bone segment
    whose vertices are nearest (limb segments by name, or the torso bones -> 'torso'); a face follows the
    majority of its vertices. Pieces simply separate at the joints when bent — schematic, no skinning."""
    from scipy.spatial import cKDTree

    names = list(limb) + ["torso"]
    trees = [cKDTree(m.vertices) for m in limb.values()] + [cKDTree(np.concatenate([t.vertices for t in torso]))]
    dist = np.stack([t.query(skin.vertices)[0] for t in trees], axis=1)
    # the torso is favoured: a limb only claims skin that is clearly closer to its own bones
    dist[:, -1] *= 0.75
    label = dist.argmin(axis=1)
    face_label = np.array([np.bincount(label[f], minlength=len(names)).argmax() for f in skin.faces])
    out = {}
    for i, n in enumerate(names):
        faces = skin.faces[face_label == i]
        if len(faces) == 0:
            continue
        m = trimesh.Trimesh(skin.vertices, faces, process=True)
        m.remove_unreferenced_vertices()
        out[n] = m
    return out
