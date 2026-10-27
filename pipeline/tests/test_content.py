"""Content consistency: pathway steps against content/structures.json and the built manifest (see content_lint.py)."""
import json

import pytest

from content_lint import MANIFEST, MISSING_PREFIX, PATHWAYS, STRUCTURES, item_keys, name_keys, parse_missing, strip_paren

PW = json.loads(PATHWAYS.read_text(encoding="utf-8"))["pathways"]
ST = {s["id"]: s for s in json.loads(STRUCTURES.read_text(encoding="utf-8"))["structures"]}
STEPS = [(pw, step) for pw in PW for step in pw["steps"]]


@pytest.fixture(scope="module")
def manifest():
    if not MANIFEST.exists():
        pytest.skip(f"{MANIFEST} is absent — run the atlas build first")
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_step_structures_exist():
    bad = [(step["id"], s["id"]) for _, step in STEPS for s in step["structures"] if s["id"] not in ST]
    assert not bad


def test_step_structures_have_meshes(manifest):
    meshed = {m["structureId"] for m in manifest["meshes"]}
    bad = sorted({s["id"] for _, step in STEPS for s in step["structures"]} - meshed)
    assert not bad


def test_missing_does_not_name_linked_structures():
    bad = []
    for _, step in STEPS:
        if "missing" not in step:
            continue
        keys = set().union(*[name_keys(ST[s["id"]]) for s in step["structures"] if s["id"] in ST])
        for _, items in parse_missing(step["missing"]["ko"]):
            bad += [(step["id"], item) for item in items if item_keys(item) & keys]
    assert not bad


def test_missing_is_one_section_with_each_name_once():
    bad = []
    for _, step in STEPS:
        if "missing" not in step:
            continue
        text = step["missing"]["ko"]
        names = [strip_paren(i) for _, items in parse_missing(text) for i in items]
        if not text.startswith(MISSING_PREFIX + " ") or "정의 없음" in text or len(names) != len(set(names)):
            bad.append((step["id"], text))
    assert not bad


def test_has3d_matches_meshes(manifest):
    meshed = {m["structureId"] for m in manifest["meshes"]}
    bad = [pw["id"] for pw in PW
           if pw.get("has3d") != any(s["id"] in meshed for step in pw["steps"] for s in step["structures"])]
    assert not bad


def test_effects_point_at_joints_and_linked_muscles(manifest):
    joints = {j["joint"] for j in manifest["joints"]}
    bad = []
    for _, step in STEPS:
        linked = {s["id"] for s in step["structures"]}
        for e in step.get("effects", []):
            if "joint" in e and e["joint"] not in joints:
                bad.append((step["id"], e))
            if "muscle" in e and e["muscle"] != "*" and e["muscle"] not in linked:
                bad.append((step["id"], e))
    assert not bad
