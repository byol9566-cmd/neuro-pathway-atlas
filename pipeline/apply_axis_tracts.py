#!/usr/bin/env python3
"""Brainstem and spinal cord fibre tracts that no open tractography atlas provides, drawn along the
neuraxis (NextBrain brainstem + Visible Human cord) at textbook cross-section positions
(atlas_pipeline/models.axis_tract), and the pathway steps that follow them.

    pipeline/.venv/bin/python pipeline/apply_axis_tracts.py [--write]

Positions are fractions of the local cross-section radius (lateral, anterior); e.g. (0.75, 0.25) is the
anterolateral funiculus. Decussations are a z band where the tract eases across the midline. Every
entry is a textbook approximation and says so in the viewer; the table is the thing for 성연 to review
(docs/data/structures-3d/axis-tracts-review.md is generated from it).
"""
import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.tracts.apply_to_content import drop_covered  # noqa: E402
from atlas_pipeline.content import (insert_after_group, link_step, load_pathways, load_structures,  # noqa: E402
                                    save_pathways, save_structures, structure_index)
REVIEW = ROOT / "docs" / "data" / "structures-3d" / "axis-tracts-review.md"

VPL = [15, -20, 5]; VPM = [17, -22, 0]
TRACTS = [
    {"id": "tr-spinothalamic-lateral", "name": {"ko": "가쪽척수시상로", "en": "Lateral spinothalamic tract"},
     "params": {"z_top": -8, "z_bottom": -230, "cross": [-215, -195], "top_point": VPL,
                "keys": [[-230, 0.45, -0.3], [-200, 0.78, 0.22], [-60, 0.8, 0.18], [-45, 0.85, 0.1], [-30, 0.6, 0.0], [-8, 0.6, 0.05]]},
     "textbook": "뒤뿔 → 앞백색맞교차에서 1~2분절 안에 교차 → 반대쪽 앞가쪽기둥 상행 → 숨뇌(올리브 가쪽, 척수섬유띠) → 다리뇌·중간뇌 덮개 가쪽(안쪽섬유띠 가쪽) → VPL. 교차 위치는 대표값(C8~T1)."},
    {"id": "tr-spinothalamic-anterior", "name": {"ko": "앞척수시상로", "en": "Anterior spinothalamic tract"},
     "params": {"z_top": -8, "z_bottom": -230, "cross": [-215, -195], "top_point": VPL,
                "keys": [[-230, 0.45, -0.3], [-200, 0.45, 0.72], [-70, 0.5, 0.65], [-55, 0.8, 0.2], [-30, 0.6, 0.0], [-8, 0.6, 0.05]]},
     "textbook": "뒤뿔 → 교차 → 반대쪽 앞기둥 상행 → 숨뇌에서 가쪽척수시상로와 합쳐 척수섬유띠 → VPL."},
    {"id": "tr-spinoreticular", "name": {"ko": "척수그물로", "en": "Spinoreticular tract"},
     "params": {"z_top": -44, "z_bottom": -400, "top_point": [6, -38, -42],
                "keys": [[-400, 0.7, 0.3], [-60, 0.7, 0.3], [-44, 0.35, 0.0]]},
     "textbook": "앞가쪽기둥을 따라 올라가 숨뇌·다리뇌 그물체(거대세포핵 등)에 양쪽으로 끝남. 그림은 같은쪽 가지."},
    {"id": "tr-trigeminothalamic", "name": {"ko": "삼차시상로 (배쪽)", "en": "Ventral trigeminothalamic tract"},
     "params": {"z_top": -6, "z_bottom": -52, "cross": [-50, -36], "top_point": VPM,
                "keys": [[-52, 0.55, -0.15], [-38, 0.3, 0.1], [-20, 0.35, 0.1], [-6, 0.4, 0.1]]},
     "textbook": "삼차신경 척수핵·주감각핵에서 나와 교차한 뒤 안쪽섬유띠 안쪽·뒤에 붙어 상행 → VPM. 교차 구간은 숨뇌~다리뇌 하부로 넓게 잡음."},
    {"id": "tr-spinocerebellar-dorsal", "name": {"ko": "뒤척수소뇌로", "en": "Dorsal (posterior) spinocerebellar tract"},
     "params": {"z_top": -56, "z_bottom": -435, "top_point": [10, -42, -46],
                "keys": [[-435, 0.8, -0.35], [-60, 0.8, -0.35], [-56, 0.75, -0.3]]},
     "textbook": "클라크기둥(C8~L3) → 같은쪽 뒤가쪽기둥 표면 → 아래소뇌다리. 교차 없음."},
    {"id": "tr-spinocerebellar-ventral", "name": {"ko": "앞척수소뇌로", "en": "Ventral (anterior) spinocerebellar tract"},
     "params": {"z_top": -24, "z_bottom": -435, "cross": [-420, -400], "top_point": [8, -40, -22],
                "keys": [[-435, 0.6, 0.0], [-400, 0.88, 0.1], [-60, 0.88, 0.1], [-40, 0.8, 0.0], [-24, 0.7, 0.0]]},
     "textbook": "척수 경계세포(L1~S2) → 앞백색맞교차 교차 → 반대쪽 가쪽기둥 앞 표면 상행 → 위소뇌다리로 들어가 소뇌 안에서 다시 교차. 두 번째 교차는 소뇌 안이라 그리지 않음."},
    {"id": "tr-vestibulospinal-lateral", "name": {"ko": "가쪽안뜰척수로", "en": "Lateral vestibulospinal tract"},
     "params": {"z_top": -42, "z_bottom": -450, "top_point": [13, -40, -40],
                "keys": [[-42, 0.55, -0.2], [-60, 0.45, 0.55], [-450, 0.4, 0.7]]},
     "textbook": "가쪽안뜰핵(Deiters) → 같은쪽 앞기둥(앞가쪽) → 척수 전장(요천수까지). 교차 없음."},
    {"id": "tr-vestibulospinal-medial", "name": {"ko": "안쪽안뜰척수로", "en": "Medial vestibulospinal tract"},
     "params": {"z_top": -45, "z_bottom": -300, "top_point": [6, -42, -44],
                "keys": [[-45, 0.2, -0.2], [-60, 0.15, 0.6], [-300, 0.15, 0.75]]},
     "textbook": "안쪽안뜰핵 → 하행 MLF(양쪽) → 앞기둥 정중선 옆 → 중간 흉수까지. 그림은 같은쪽 가지."},
    {"id": "tr-reticulospinal-pontine", "name": {"ko": "다리뇌그물척수로", "en": "Pontine (medial) reticulospinal tract"},
     "params": {"z_top": -30, "z_bottom": -470, "top_point": [5, -34, -30],
                "keys": [[-30, 0.2, -0.05], [-60, 0.3, 0.6], [-470, 0.3, 0.75]]},
     "textbook": "다리뇌 그물체(입쪽·꼬리쪽 다리뇌그물핵) → 같은쪽 앞기둥 안쪽 → 척수 전장."},
    {"id": "tr-reticulospinal-medullary", "name": {"ko": "숨뇌그물척수로", "en": "Medullary (lateral) reticulospinal tract"},
     "params": {"z_top": -42, "z_bottom": -470, "top_point": [3, -36, -42],
                "keys": [[-42, 0.3, 0.0], [-60, 0.65, 0.3], [-470, 0.7, 0.3]]},
     "textbook": "거대세포그물핵 → 주로 같은쪽(일부 반대쪽) 가쪽기둥 앞부분 → 척수 전장. 그림은 같은쪽."},
    {"id": "tr-tectospinal", "name": {"ko": "덮개척수로", "en": "Tectospinal tract"},
     "params": {"z_top": -4, "z_bottom": -200, "cross": [-16, -8], "top_point": [6, -32, -2],
                "keys": [[-4, 0.3, 0.0], [-20, 0.15, 0.1], [-45, 0.15, 0.45], [-60, 0.2, 0.8], [-200, 0.2, 0.8]]},
     "textbook": "위둔덕 → 등쪽덮개교차(중간뇌) → 반대쪽 앞기둥 정중선 옆(MLF 앞) → 경수(C4 부근)까지."},
    {"id": "tr-rubrospinal", "name": {"ko": "적색핵척수로", "en": "Rubrospinal tract"},
     "params": {"z_top": -8, "z_bottom": -150, "cross": [-16, -9], "top_point": [6, -20, -6],
                "keys": [[-8, 0.3, 0.1], [-30, 0.6, -0.1], [-55, 0.7, -0.05], [-60, 0.75, -0.05], [-150, 0.75, -0.05]]},
     "textbook": "적색핵(큰세포부) → 배쪽덮개교차 → 반대쪽 다리뇌·숨뇌 가쪽덮개 → 가쪽기둥(가쪽겉질척수로 앞) → 사람에서는 경수 상부까지만."},
]
# step id -> [(structure id, side)] — the side is the tract's side above its decussation (thalamic side of an ascending tract, nucleus side of a descending one)
STEP_TRACTS = {
    "spinothalamic-lateral-2": [("tr-spinothalamic-lateral", "contra")],
    "spinothalamic-anterior-2": [("tr-spinothalamic-anterior", "contra")],
    "spinoreticular-2": [("tr-spinoreticular", "ipsi")],
    "trigeminal-touch-2": [("tr-trigeminothalamic", "contra")],
    "trigeminal-pain-2": [("tr-trigeminothalamic", "contra")],
    "spinocerebellar-dorsal-2": [("tr-spinocerebellar-dorsal", "ipsi")],
    "spinocerebellar-ventral-2": [("tr-spinocerebellar-ventral", "contra")],
    "vestibulospinal-lateral-2": [("tr-vestibulospinal-lateral", "ipsi")],
    "vestibulospinal-medial-2": [("tr-vestibulospinal-medial", "ipsi")],
    "reticulospinal-pontine-2": [("tr-reticulospinal-pontine", "ipsi")],
    "reticulospinal-medullary-2": [("tr-reticulospinal-medullary", "ipsi")],
    "tectospinal-2": [("tr-tectospinal", "ipsi")],
    "rubrospinal-2": [("tr-rubrospinal", "ipsi")],
}
COVERED = {
    "tr-spinothalamic-lateral": ["척수 앞백색맞교차", "앞백색맞교차", "가쪽척수시상로"],
    "tr-spinothalamic-anterior": ["척수 앞백색맞교차", "앞백색맞교차", "앞척수시상로"],
    "tr-trigeminothalamic": ["삼차시상로"], "tr-spinoreticular": ["척수그물로"],
    "tr-spinocerebellar-dorsal": ["뒤척수소뇌로"], "tr-spinocerebellar-ventral": ["앞척수소뇌로"],
    "tr-vestibulospinal-lateral": ["가쪽안뜰척수로"], "tr-vestibulospinal-medial": ["안쪽안뜰척수로"],
    "tr-reticulospinal-pontine": ["다리뇌그물척수로"], "tr-reticulospinal-medullary": ["숨뇌그물척수로"],
    "tr-tectospinal": ["덮개척수로"], "tr-rubrospinal": ["적색핵척수로"],
}
NOTE = "교과서 기하: 뇌줄기 축(NextBrain)과 척수 축(Visible Human)을 따라 교과서 단면도의 위치에 그린 섬유로. 트랙토그래피 데이터가 아니며 교차 위치는 대표값이다."


def main(write):
    s = load_structures()
    by_id = structure_index(s)
    for t in TRACTS:
        entry = {"id": t["id"], "group": "tracts", "tract": True, "name": t["name"],
                 "source": {"atlas": "model", "shape": "axis-tract", "params": t["params"], "centreMni": [0, 0, 0], "bilateral": True,
                            "modelNote": NOTE + " " + t["textbook"]}}
        if t["id"] in by_id:
            by_id[t["id"]].update(entry)
        else:
            insert_after_group(s["structures"], "tracts", entry); by_id[t["id"]] = entry
    p = load_pathways()
    changed = []
    for pw in p["pathways"]:
        for st in pw["steps"]:
            for sid, side in STEP_TRACTS.get(st["id"], []):
                if "missing" in st:
                    cleaned = drop_covered(st["missing"]["ko"], COVERED.get(sid, []))
                    if cleaned:
                        st["missing"]["ko"] = cleaned
                    else:
                        del st["missing"]
                if link_step(p, st["id"], sid, side, "front"):
                    changed.append((pw["id"], st["id"], sid, side))
    print(f"{len(TRACTS)} axis tracts; steps:", *changed, sep="\n  ")
    rows = [f"# 뇌줄기·척수 섬유로 — 교과서 기하 표 (성연 검수용, {datetime.date.today().isoformat()})", "",
            "뷰어의 경로 재생이 이 선을 따른다. 위치는 단면 반지름에 대한 비율(가쪽, 앞쪽), 교차는 z 구간(MNI mm). 틀린 곳을 적어 주면 표만 고치면 된다(`pipeline/apply_axis_tracts.py`).", "",
            "| id | 이름 | 범위 z | 교차 z | 단면 위치 키프레임 (z: 가쪽, 앞) | 교과서 주행 요약 |", "|---|---|---|---|---|---|"]
    for t in TRACTS:
        pr = t["params"]
        keys = "; ".join(f"{int(k[0])}: {k[1]:+.2f}, {k[2]:+.2f}" for k in pr["keys"])
        rows.append(f"| {t['id']} | {t['name']['ko']} | {pr['z_top']} ~ {pr['z_bottom']} | {pr.get('cross', '—')} | {keys} | {t['textbook']} |")
    if write:
        save_structures(s)
        save_pathways(p)
        REVIEW.write_text("\n".join(rows) + "\n", encoding="utf-8")
        print("written")


if __name__ == "__main__":
    main("--write" in sys.argv)
