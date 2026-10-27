#!/usr/bin/env python3
"""Autonomic nerves outside the CNS, drawn on the body: the sympathetic trunk alongside the vertebral
bodies (from the BodyParts3D canal axis), its cervical continuation to the superior cervical ganglion and
the internal carotid plexus to the eye, the greater splanchnic nerve to the celiac ganglion and adrenal
medulla, cardiac nerves to the heart, the hypogastric route to the bladder, and the pelvic splanchnic
nerves (S2-4) to the bladder. Positions are textbook relations to structures we have; the viewer says so.

    pipeline/.venv/bin/python pipeline/apply_autonomic.py [--write]
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
STRUCTURES = ROOT / "content" / "structures.json"
PATHWAYS = ROOT / "content" / "pathways.json"
MANIFEST = ROOT / "viewer" / "public" / "data" / "manifest.json"
CANAL = ROOT / "data" / "derived" / "bp3d" / "canal_axis.json"
NOTE = "기하 모형: 공개 3D 데이터가 없는 자율신경 주행을 BodyParts3D 몸(척추관 축·장기 위치)과 교과서 관계로 그린 관."


def canal():
    rows = sorted(json.loads(CANAL.read_text())["points"], key=lambda r: -r["z"])
    z = np.array([r["z"] for r in rows]); x = np.array([r["x"] for r in rows]); y = np.array([r["y"] for r in rows])
    return lambda zq: (float(np.interp(-zq, -z, x)), float(np.interp(-zq, -z, y)))


def main(write):
    if not MANIFEST.exists():  # organ positions come from the built atlas (for now)
        sys.exit(f"{MANIFEST} is missing: run a full build first (PYTHONPATH=pipeline pipeline/.venv/bin/python -m atlas_pipeline.build)")
    cen = {m["id"]: np.array(m["centroid"]) for m in json.loads(MANIFEST.read_text())["meshes"]}
    c = canal()
    # the paravertebral trunk: beside the vertebral bodies, ~22 mm lateral of the canal and ~28 mm in front
    trunk = [[c(z)[0] + 22, c(z)[1] + 28, float(z)] for z in range(-120, -560, -20)]
    scg = cen["pn-superior-cervical.R"]; iris = cen["so-iris.R"]
    heart = cen["vs-heart.M"]; adrenal = cen["vs-adrenal.R"]; bladder = cen["vs-bladder.M"]; prostate = cen["vs-prostate.M"]
    celiac = [10.0, c(-470)[1] + 60, -470.0]  # celiac ganglion: in front of the aorta at L1
    hypogastric = [8.0, c(-560)[1] + 40, -600.0]
    nerves = [
        ("pn-sympathetic-trunk", {"ko": "교감신경줄기 (척추옆신경절 사슬)", "en": "Sympathetic trunk"}, 1.3,
         [list(scg), [22, c(-120)[1] + 24, -120.0]] + trunk,
         "위목신경절에서 경추·흉추·요추 옆을 따라 내려가는 척추옆 신경절 사슬. 신경절(별·중간목·흉추 12·요추 4·엉치)은 사슬 위의 결절로 생각하면 된다."),
        ("pn-internal-carotid-plexus", {"ko": "속목동맥신경얼기 (→ 동공확대근)", "en": "Internal carotid plexus"}, 0.6,
         [list(scg), [20, -10, -60], [16, 6, -40], [15, 12, -30], [20, 26, -29], [26, 40, -34], [float(iris[0]), float(iris[1]) - 4, float(iris[2])]],
         "위목신경절 절후섬유가 속목동맥을 타고 두개 안으로 → 해면정맥굴 → 눈신경·긴섬모체신경을 따라 동공확대근(·위눈꺼풀판근)."),
        ("pn-cardiac-nerves", {"ko": "심장신경 (교감)", "en": "Cardiac sympathetic nerves"}, 0.8,
         [trunk[3], [10, trunk[3][1] + 30, -230.0], [-5, heart[1] + 10, heart[2] + 40], list(heart)],
         "경추·상부 흉추 신경절(별신경절 포함)의 절후섬유가 심장신경얼기를 거쳐 심장으로."),
        ("pn-greater-splanchnic", {"ko": "큰내장신경 (T5~9 → 복강신경절)", "en": "Greater splanchnic nerve"}, 0.9,
         [trunk[8], trunk[11], [16, c(-400)[1] + 45, -420.0], celiac],
         "T5~T9 신경절을 통과한 절전섬유가 가로막을 뚫고 복강신경절(척추앞신경절)로."),
        ("pn-celiac-ganglion", {"ko": "복강신경절", "en": "Celiac ganglion"}, None, celiac,
         "복강동맥 기시부 양옆의 척추앞신경절. 복부 내장 교감 절후뉴런."),
        ("pn-adrenal-branch", {"ko": "부신속질 가지 (절전)", "en": "Preganglionic fibres to the adrenal medulla"}, 0.6,
         [celiac, [22, (celiac[1] + adrenal[1]) / 2, -465.0], list(adrenal)],
         "큰내장신경의 절전섬유가 복강신경절을 지나쳐 부신속질 크롬친화세포에 직접 시냅스."),
        ("pn-hypogastric", {"ko": "아랫배신경·아래아랫배신경얼기 (→ 방광)", "en": "Hypogastric nerves and inferior hypogastric plexus"}, 0.7,
         [trunk[-2], [8, c(-560)[1] + 25, -570.0], hypogastric, list(bladder)],
         "요추 내장신경 → 위아랫배신경얼기(대동맥 갈림) → 아랫배신경 → 아래아랫배신경얼기 → 방광·전립샘(저장·사정)."),
        ("pn-pelvic-splanchnic", {"ko": "골반내장신경 (S2~4 부교감)", "en": "Pelvic splanchnic nerves"}, 0.7,
         [[6, c(-560)[1], -560.0], [12, c(-560)[1] + 30, -610.0], [10, bladder[1] - 20, bladder[2] + 30], [float(bladder[0]) + 10, float(bladder[1]) - 15, float(bladder[2])]],
         "S2~S4 절전섬유가 아래아랫배신경얼기로 → 방광벽 신경절 → 배뇨근 수축(배뇨), 발기."),
    ]
    data = json.loads(STRUCTURES.read_text(encoding="utf-8"))
    by_id = {x["id"]: x for x in data["structures"]}
    anchor = max(i for i, x in enumerate(data["structures"]) if x["group"] == "peripheral")
    # nerves to a midline organ: the left copy keeps the organ end un-mirrored so both sides reach it
    fixed_tail = {"pn-cardiac-nerves": 1, "pn-hypogastric": 1}
    for sid, name, radius, pts, text in nerves:
        if radius is None:
            src = {"atlas": "model", "shape": "ellipsoid", "params": {"radii": [6, 4, 10]}, "centreMni": [round(v, 1) for v in pts], "axis": [0, 0, 1], "bilateral": True, "modelNote": NOTE + " " + text}
        else:
            src = {"atlas": "model", "shape": "path-tube", "params": {"radius": radius, "points": [[round(float(v), 1) for v in p] for p in pts]}, "centreMni": [0, 0, 0], "bilateral": True, "modelNote": NOTE + " " + text}
            if sid in fixed_tail:
                src["params"]["mirrorFixedTail"] = fixed_tail[sid]
        entry = {"id": sid, "group": "peripheral", "name": name, "source": src}
        if sid in by_id:
            by_id[sid].update(entry)
        else:
            anchor += 1; data["structures"].insert(anchor, entry); by_id[sid] = entry
    steps = {
        "sympathetic-somatic-2": [("pn-sympathetic-trunk", "ipsi")],
        "sympathetic-thoracic-1": [("pn-sympathetic-trunk", "ipsi")],
        "sympathetic-thoracic-2": [("pn-cardiac-nerves", "ipsi")],
        "sympathetic-abdominopelvic-1": [("pn-sympathetic-trunk", "ipsi"), ("pn-greater-splanchnic", "ipsi")],
        "sympathetic-abdominopelvic-2": [("pn-celiac-ganglion", "ipsi")],
        "sympathetic-abdominopelvic-3": [("pn-hypogastric", "ipsi")],
        "sympathetic-adrenal-1": [("pn-greater-splanchnic", "ipsi"), ("pn-adrenal-branch", "ipsi")],
        "sympathetic-head-neck-1": [("pn-sympathetic-trunk", "ipsi")],
        "sympathetic-head-neck-2": [("pn-internal-carotid-plexus", "ipsi")],
        "autonomic-pupil-dilation-2": [("pn-sympathetic-trunk", "ipsi")],
        "autonomic-pupil-dilation-3": [("pn-internal-carotid-plexus", "ipsi")],
        "sympathetic-sweat-1": [("pn-sympathetic-trunk", "ipsi")],
        "vestibulo-autonomic-3": [("pn-sympathetic-trunk", "ipsi")],
        "baroreflex-sympathetic-4": [("pn-sympathetic-trunk", "ipsi")],
        "parasympathetic-sacral-2": [("pn-pelvic-splanchnic", "ipsi")],
        "autonomic-micturition-2": [("pn-pelvic-splanchnic", "ipsi")],
        "autonomic-micturition-1": [("pn-hypogastric", "ipsi")],
        "autonomic-sexual-1": [("pn-pelvic-splanchnic", "ipsi")],
        "autonomic-sexual-2": [("pn-hypogastric", "ipsi")],
    }
    p = json.loads(PATHWAYS.read_text(encoding="utf-8"))
    changed = 0
    for pw in p["pathways"]:
        for st in pw["steps"]:
            for sid, side in steps.get(st["id"], []):
                if not any(r["id"] == sid for r in st["structures"]):
                    st["structures"].insert(0, {"id": sid, "side": side}); changed += 1
    print(f"{len(nerves)} autonomic structures, {changed} step links")
    if write:
        STRUCTURES.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if changed:
            PATHWAYS.write_text(json.dumps(p, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("written")


if __name__ == "__main__":
    main("--write" in sys.argv)
