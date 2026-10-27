"""content/structures.json and content/pathways.json as the apply_* / integrate_* scripts edit them, and the
mesh-cache centroids some of them place their models by.

Saving writes exactly the bytes the scripts always wrote (UTF-8, indent 2, trailing newline), so a re-run
that changes nothing leaves the files byte-identical.
"""
import json

from . import CONTENT_DIR, REPO_ROOT

STRUCTURES = CONTENT_DIR / "structures.json"
PATHWAYS = CONTENT_DIR / "pathways.json"
MESH_CACHE = REPO_ROOT / "data" / "derived" / "meshes"  # build.py: <meshId>.ply + .json, structures/<id>.json
BUILD_CMD = "PYTHONPATH=pipeline pipeline/.venv/bin/python -m atlas_pipeline.build"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_structures():
    return _load(STRUCTURES)


def load_pathways():
    return _load(PATHWAYS)


def save_structures(data):
    _save(STRUCTURES, data)


def save_pathways(data):
    _save(PATHWAYS, data)


def structure_index(structures):
    """structure id -> entry (the same dicts, so updates land in the list); takes the loaded file or its list"""
    if isinstance(structures, dict):
        structures = structures["structures"]
    return {s["id"]: s for s in structures}


def insert_after_group(structures_list, group, new_struct):
    """insert after the last current member of `group` (successive inserts of that group keep their order)"""
    anchor = max(i for i, x in enumerate(structures_list) if x["group"] == group)
    structures_list.insert(anchor + 1, new_struct)


def link_step(pathways, step_id, structure_id, side, position="append"):
    """add {"id": structure_id, "side": side} to a pathway step's structures, at the end ('append') or the
    start ('front'). No-op if the step already names the structure; KeyError if no step has that id.
    -> True if added"""
    for pw in pathways["pathways"]:
        for st in pw["steps"]:
            if st["id"] != step_id:
                continue
            if any(r["id"] == structure_id for r in st["structures"]):
                return False
            ref = {"id": structure_id, "side": side}
            if position == "front":
                st["structures"].insert(0, ref)
            elif position == "append":
                st["structures"].append(ref)
            else:
                raise ValueError(f"position must be 'append' or 'front', not {position!r}")
            return True
    raise KeyError(f"no pathway step {step_id!r} in {PATHWAYS.name}")


def cached_centroids():
    """mesh id -> centroid (RAS mm) from the mesh cache the last build wrote (data/derived/meshes); exits
    with the build command if there is no cache yet"""
    recs = sorted(MESH_CACHE.glob("*.json"))
    if not recs:
        raise SystemExit(f"{MESH_CACHE} has no mesh records: run a full build first ({BUILD_CMD}), "
                         "then this script, then `--only <ids>` for the structures it changed")
    return {p.stem: json.loads(p.read_text(encoding="utf-8"))["centroid"] for p in recs}
