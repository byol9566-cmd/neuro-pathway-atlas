#!/usr/bin/env python3
"""Cranial nerve courses outside the brainstem as waypoint tubes (atlas_pipeline/models.path_tube), and
the pathway steps that follow them.

    pipeline/.venv/bin/python pipeline/apply_cranial_nerves.py [--write]

Waypoints are textbook anatomy in MNI RAS for the right side (the left is mirrored): nucleus (taken from
the nucleus mesh's centroid in the mesh cache, data/derived/meshes, so a full build must come first and
`build --only <these nerve ids>` after) -> brainstem exit -> skull-base foramen ->
ganglion / target. No open 3D data gives these courses; the review sheet
docs/data/structures-3d/cranial-nerves-review.md lists every waypoint for 성연.
"""
import sys
from pathlib import Path

from atlas_pipeline.content import (cached_centroids, insert_after_group, link_step, load_pathways,
                                    load_structures, save_pathways, save_structures, structure_index)

ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / "docs" / "data" / "structures-3d" / "cranial-nerves-review.md"

# landmarks (right side, RAS mm) — foramina read from textbook relations to structures we have
SOF = [20, 26, -27]          # superior orbital fissure
ROTUNDUM = [22, 8, -40]      # foramen rotundum
OVALE = [24, -2, -46]        # foramen ovale
IAM = [30, -30, -25]         # internal acoustic meatus
STYLOMASTOID = [42, -28, -52]
JUGULAR = [23, -34, -60]     # jugular foramen
HYPOGLOSSAL_CANAL = [18, -32, -62]
CAVERNOUS = [15, 8, -26]     # lateral wall of the cavernous sinus

NERVES = [
    {"id": "pn-cn4", "name": {"ko": "도르래신경 (IV)", "en": "Trochlear nerve"}, "radius": 0.8, "nucleus": ("bs-trochlear", "contra"),
     "points": [[-3.5, -28, -10], [-2, -36, -13], [0, -40, -14], [4, -40, -14], [16, -30, -16], [20, -14, -20], [16, 6, -24], SOF, [22, 40, -20]],
     "textbook": "핵(반대쪽) → 중간뇌 등쪽에서 아래둔덕 아래로 나오며 교차 → 대뇌다리를 돌아 앞으로 → 해면정맥굴 가쪽벽 → 위안와틈새 → 위빗근. 유일하게 등쪽으로 나와 교차하는 뇌신경."},
    {"id": "pn-cn5", "name": {"ko": "삼차신경 뿌리 (V)", "en": "Trigeminal nerve root"}, "radius": 1.6, "nucleus": ("bs-trigeminal-motor", "ipsi"),
     "points": [[7, -38, -36], [14, -36, -34], [20, -28, -33], [20, -16, -32]],
     "textbook": "다리뇌 가쪽에서 큰 감각뿌리·작은 운동뿌리로 나와 바위뼈 끝(Meckel 동굴)의 삼차신경절로."},
    {"id": "pn-cn5-v1", "name": {"ko": "눈신경 (V1)", "en": "Ophthalmic nerve"}, "radius": 1.0,
     "points": [[18, -6, -31], [17, 6, -26], SOF, [24, 42, -24]],
     "textbook": "삼차신경절 → 해면정맥굴 가쪽벽 → 위안와틈새 → 안와(이마·눈물·코섬모체신경)."},
    {"id": "pn-cn5-v2", "name": {"ko": "위턱신경 (V2)", "en": "Maxillary nerve"}, "radius": 1.0,
     "points": [[20, -6, -33], [21, 2, -37], ROTUNDUM, [26, 20, -46], [28, 42, -38]],
     "textbook": "삼차신경절 → 원형구멍 → 날개입천장오목 → 아래안와신경으로 얼굴 중앙."},
    {"id": "pn-cn5-v3", "name": {"ko": "아래턱신경 (V3)", "en": "Mandibular nerve"}, "radius": 1.2,
     "points": [[22, -8, -35], OVALE, [30, -4, -60], [40, 8, -74]],
     "textbook": "삼차신경절 → 타원구멍 → 관자밑오목(씹기근 운동가지·귀관자·혀·아래이틀신경) → 아래턱."},
    {"id": "pn-cn6", "name": {"ko": "갓돌림신경 (VI)", "en": "Abducens nerve"}, "radius": 0.8, "nucleus": ("bs-abducens", "ipsi"),
     "points": [[4, -42, -40], [4, -33, -47], [6, -20, -42], [10, -4, -32], CAVERNOUS, SOF, [32, 38, -25]],
     "textbook": "핵 → 다리뇌숨뇌이음부 앞쪽으로 나옴 → 경사대를 따라 올라가 Dorello관 → 해면정맥굴 안(속목동맥 가쪽) → 위안와틈새 → 가쪽곧은근."},
    {"id": "pn-cn7-peripheral", "name": {"ko": "얼굴신경 (VII) 말초", "en": "Facial nerve, peripheral course"}, "radius": 1.1,
     "points": [[8, -38, -40], [18, -34, -32], IAM, [35, -28, -22], [40, -30, -34], [41, -29, -45], STYLOMASTOID, [50, -14, -56], [48, 10, -48]],
     "textbook": "다리뇌숨뇌이음부에서 나와 속귀길 → 무릎신경절(얼굴신경관 첫 굽이) → 고실 안쪽벽을 따라 뒤로 → 꼭지돌기 안에서 내려와 붓꼭지구멍 → 귀밑샘 안 신경얼기 → 표정근."},
    {"id": "pn-greater-petrosal", "name": {"ko": "큰바위신경", "en": "Greater petrosal nerve"}, "radius": 0.6,
     "points": [[35, -28, -22], [30, -18, -30], [26, 4, -40], [24, 20, -44]],
     "textbook": "무릎신경절에서 앞안쪽으로 → 큰바위신경구멍·찢긴구멍 위 → 날개관신경 → 날개입천장신경절(눈물·코·입천장샘 절전섬유)."},
    {"id": "pn-chorda-tympani", "name": {"ko": "고실끈신경", "en": "Chorda tympani"}, "radius": 0.5,
     "points": [[41, -29, -45], [38, -22, -42], [34, -10, -52], [33, 4, -68], [33, 12, -76]],
     "textbook": "붓꼭지구멍 위에서 얼굴신경을 떠나 고실을 가로질러 → 바위고실틈새 → 혀신경에 합류 → 턱밑신경절(침샘 절전) / 혀 앞 2/3 미각."},
    {"id": "pn-cn9", "name": {"ko": "혀인두신경 (IX)", "en": "Glossopharyngeal nerve"}, "radius": 0.9, "nucleus": ("bs-ambiguus", "ipsi"),
     "points": [[5, -42, -51], [14, -38, -52], JUGULAR, [20, -30, -64], [28, -14, -72], [24, 8, -78]],
     "textbook": "숨뇌 올리브 뒤고랑에서 나와 → 목정맥구멍(위·아래신경절) → 붓인두근 바깥을 돌아 앞으로 → 인두·혀 뒤 1/3."},
    {"id": "pn-lesser-petrosal", "name": {"ko": "작은바위신경 (고실신경얼기 경유)", "en": "Lesser petrosal nerve"}, "radius": 0.5,
     "points": [[20, -31, -62], [30, -30, -48], [32, -24, -38], [28, -12, -44], [24, -6, -50]],
     "textbook": "IX 아래신경절 → 고실신경 → 고실신경얼기(가운데귀 안쪽벽) → 작은바위신경 → 타원구멍 옆으로 나와 귀신경절(귀밑샘 절전)."},
    {"id": "pn-cn10", "name": {"ko": "미주신경 (X)", "en": "Vagus nerve"}, "radius": 1.2, "nucleus": ("bs-dorsal-vagal", "ipsi"),
     "points": [[4, -45, -53], [14, -38, -54], JUGULAR, [18, -26, -64], [20, -28, -90], [18, -30, -130], [12, -34, -180]],
     "textbook": "숨뇌 올리브 뒤고랑 → 목정맥구멍(위·아래(결절)신경절) → 목동맥집 안(속목정맥·목동맥 사이 뒤) → 가슴으로."},
    {"id": "pn-cn11", "name": {"ko": "더부신경 (XI)", "en": "Accessory nerve"}, "radius": 0.9, "nucleus": ("bs-accessory", "ipsi"),
     "points": [[4.5, -40, -62], [10, -38, -70], [12, -36, -62], JUGULAR, [34, -40, -72], [46, -44, -95], [55, -70, -120]],
     "textbook": "척수 C1~C5 더부신경핵 → 큰구멍으로 올라와 → 목정맥구멍 → 목빗근 → 뒤목삼각 → 등세모근."},
    {"id": "pn-cn12", "name": {"ko": "혀밑신경 (XII)", "en": "Hypoglossal nerve"}, "radius": 0.9, "nucleus": ("bs-hypoglossal", "ipsi"),
     "points": [[2.7, -45, -51], [8, -37, -55], HYPOGLOSSAL_CANAL, [24, -26, -76], [30, -8, -84], [22, 14, -78]],
     "textbook": "숨뇌 올리브 앞고랑 → 혀밑신경관 → 목동맥·목정맥 사이로 내려와 앞으로 굽어 → 혀근육."},
    {"id": "pn-short-ciliary", "name": {"ko": "짧은섬모체신경", "en": "Short ciliary nerves"}, "radius": 0.4,
     "points": [[29, 38, -28], [31, 46, -31], [32, 52, -34]],
     "textbook": "섬모체신경절 → 안구 뒤극을 뚫고 들어가 동공조임근·섬모체근(절후 부교감)."},
]
STEP_NERVES = {
    "cranial-iv-motor-2": [("pn-cn4", "ipsi")],
    "cranial-v-motor-2": [("pn-cn5", "ipsi"), ("pn-cn5-v3", "ipsi")],
    "cranial-vi-motor-2": [("pn-cn6", "ipsi")],
    "cranial-vii-motor-2": [("pn-cn7-peripheral", "ipsi")],
    "cranial-ix-x-motor-2": [("pn-cn9", "ipsi"), ("pn-cn10", "ipsi")],
    "cranial-xi-motor-2": [("pn-cn11", "ipsi")],
    "cranial-xii-motor-2": [("pn-cn12", "ipsi")],
    "corneal-reflex-1": [("pn-cn5-v1", "ipsi"), ("pn-cn5", "ipsi")],
    "corneal-reflex-3": [("pn-cn7-peripheral", "ipsi")],
    "acoustic-attenuation-reflex-3": [("pn-cn7-peripheral", "ipsi")],
    "jaw-jerk-3": [("pn-cn5-v3", "ipsi")],
    "jaw-opening-reflex-1": [("pn-cn5-v3", "ipsi")],
    "gag-reflex-1": [("pn-cn9", "ipsi")],
    "gag-reflex-3": [("pn-cn10", "ipsi")],
    "cough-reflex-3": [("pn-cn10", "ipsi")],
    "swallowing-reflex-3": [("pn-cn10", "ipsi")],
    "pupillary-light-reflex-4": [("pn-short-ciliary", "ipsi")],
    "hvor-inhibition-2": [("pn-cn6", "ipsi")],
    "facial-lacrimation-1": [("pn-cn7-peripheral", "ipsi")],
    "facial-lacrimation-2": [("pn-greater-petrosal", "ipsi")],
    "facial-salivation-1": [("pn-cn7-peripheral", "ipsi")],
    "facial-salivation-2": [("pn-chorda-tympani", "ipsi")],
    "glossopharyngeal-salivation-1": [("pn-cn9", "ipsi")],
    "glossopharyngeal-salivation-2": [("pn-lesser-petrosal", "ipsi")],
    "vagal-parasympathetic-1": [("pn-cn10", "ipsi")],
    "baroreflex-vagal-3": [("pn-cn10", "ipsi")],
    "gustatory-central-1": [("pn-chorda-tympani", "ipsi")],
}
NOTE = "기하 모형: 교과서 주행의 경유점(핵·뇌줄기 출구·두개저 구멍·신경절·표적)을 이은 관. 공개 3D 데이터가 없어 위치는 교과서 관계에서 추정했다."


def main(write):
    s = load_structures()
    by_id = structure_index(s)
    cent = cached_centroids()
    for n in NERVES:
        pts = [list(map(float, p)) for p in n["points"]]
        if n.get("nucleus"):
            nid, rel = n["nucleus"]
            c = cent.get(f"{nid}.{'L' if rel == 'contra' else 'R'}")
            if c:
                pts[0] = [round(v, 2) for v in c]  # start exactly at the nucleus mesh
        entry = {"id": n["id"], "group": "peripheral", "name": n["name"],
                 "source": {"atlas": "model", "shape": "path-tube", "params": {"radius": n["radius"], "points": pts}, "centreMni": [0, 0, 0],
                            "bilateral": True, "modelNote": NOTE + " " + n["textbook"]}}
        if n["id"] in by_id:
            by_id[n["id"]].update(entry)
        else:
            insert_after_group(s["structures"], "peripheral", entry); by_id[n["id"]] = entry
    p = load_pathways()
    changed = []
    for pw in p["pathways"]:
        for st in pw["steps"]:
            for sid, side in STEP_NERVES.get(st["id"], []):
                if link_step(p, st["id"], sid, side):  # the nerve comes after the nucleus
                    changed.append((pw["id"], st["id"], sid, side))
    print(f"{len(NERVES)} nerves; steps:", *changed, sep="\n  ")
    rows = ["# 뇌신경 주행 경유점 표 (성연 검수용, 2026-10-05)", "",
            "오른쪽 기준 MNI RAS mm. 첫 점은 핵 메시의 무게중심(있으면). 틀린 점을 적어 주면 `pipeline/apply_cranial_nerves.py`의 표만 고친다.", "",
            "| id | 이름 | 경유점 (x, y, z) | 교과서 주행 |", "|---|---|---|---|"]
    for n in NERVES:
        rows.append(f"| {n['id']} | {n['name']['ko']} | " + " → ".join(f"({p[0]:g}, {p[1]:g}, {p[2]:g})" for p in by_id[n['id']]['source']['params']['points']) + f" | {n['textbook']} |")
    if write:
        save_structures(s)
        save_pathways(p)
        REVIEW.write_text("\n".join(rows) + "\n", encoding="utf-8")
        print("written")


if __name__ == "__main__":
    main("--write" in sys.argv)
