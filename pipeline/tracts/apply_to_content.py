#!/usr/bin/env python3
"""Register the prepared HCP1065 tracts in content/: new tract structures, centerline overrides for the
NextBrain tract labels, and the pathway steps that should follow them.

    pipeline/.venv/bin/python pipeline/tracts/apply_to_content.py [--write]

Idempotent: structures already present are updated in place, pathway steps get a tract only once.
Which steps get which tract is an explicit table below (the steps' `missing` text names the tract), not a
keyword match — '활꼴' also matches the arcuate *nucleus*.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STRUCTURES = ROOT / "content" / "structures.json"
PATHWAYS = ROOT / "content" / "pathways.json"

NEW_STRUCTURES = [
    {"id": "tr-cst-cerebral", "name": {"ko": "겉질척수로 (방사관·속섬유막·대뇌다리 구간)", "en": "Corticospinal tract, cerebral course"},
     "tracts": {"L": "cst-cerebral-l", "R": "cst-cerebral-r"},
     "note": "HCP1065 겉질척수 다발의 겉질~위다리뇌 구간. 숨뇌 피라미드는 NextBrain 라벨(tr-pyramid)."},
    {"id": "tr-cst-lateral", "name": {"ko": "가쪽겉질척수로", "en": "Lateral corticospinal tract"},
     "tracts": {"L": "cst-lateral-l", "R": "cst-lateral-r"},
     "note": "피라미드교차 뒤 반대쪽 다발의 연속. 교차와 가쪽기둥 위치는 교과서 기하, 척수 축은 Visible Human 척수."},
    {"id": "tr-cst-anterior", "name": {"ko": "앞겉질척수로", "en": "Anterior corticospinal tract"},
     "tracts": {"L": "cst-anterior-l", "R": "cst-anterior-r"},
     "note": "교차하지 않은 같은 쪽 다발의 앞기둥 연속(~T1까지). 앞기둥 위치는 교과서 기하."},
    {"id": "tr-corticobulbar", "name": {"ko": "겉질숨뇌로", "en": "Corticobulbar tract"},
     "tracts": {"L": "cbt-l", "R": "cbt-r"}},
    {"id": "tr-optic-radiation", "name": {"ko": "시각부챗살", "en": "Optic radiation"},
     "tracts": {"L": "or-l", "R": "or-r"}},
    {"id": "tr-arcuate", "name": {"ko": "활꼴다발", "en": "Arcuate fasciculus"},
     "tracts": {"L": "af-l", "R": "af-r"}},
    {"id": "tr-uncinate", "name": {"ko": "갈고리다발", "en": "Uncinate fasciculus"},
     "tracts": {"L": "uf-l", "R": "uf-r"}},
    {"id": "tr-cingulum", "name": {"ko": "띠다발", "en": "Cingulum bundle"},
     "tracts": {"L": "cingulum-l", "R": "cingulum-r"},
     "note": "HCP1065의 이마–해마곁 띠다발(C_FPH)."},
]
CENTERLINE_FROM = {
    "tr-medial-lemniscus": {"L": "ml-l", "R": "ml-r"},
    "tr-icp": {"L": "icp-l", "R": "icp-r"},
    "tr-fornix": {"L": "fornix-l", "R": "fornix-r"},
}
# step id -> (structure id, side). The side follows the structure the step already names.
STEP_TRACTS = {
    "corticospinal-lateral-1": ("tr-cst-cerebral", "ipsi"),
    "corticospinal-lateral-3": ("tr-cst-lateral", "contra"),
    "corticospinal-anterior-1": ("tr-cst-cerebral", "ipsi"),
    "corticospinal-anterior-3": ("tr-cst-anterior", "ipsi"),
    "cerebellar-double-crossing-2": ("tr-cst-lateral", "contra"),
    "corticobulbar-1": ("tr-corticobulbar", "ipsi"),
    "language-spoken-4": ("tr-corticobulbar", "ipsi"),
    "language-written-4": ("tr-corticobulbar", "ipsi"),
    "visual-temporal-3": ("tr-optic-radiation", "ipsi"),
    "visual-nasal-3": ("tr-optic-radiation", "contra"),
    "papez-5": ("tr-cingulum", "ipsi"),
    "association-cingulum-2": ("tr-cingulum", "ipsi"),
    "association-uncinate-2": ("tr-uncinate", "ipsi"),
    "language-spoken-3": ("tr-arcuate", "ipsi"),
    "language-dorsal-2": ("tr-arcuate", "ipsi"),
    "language-written-3": ("tr-arcuate", "ipsi"),
}


# names the steps' `missing` text uses for things a tract now covers
COVERED_NAMES = {
    "tr-cst-cerebral": ["속섬유막 뒤다리", "속섬유막", "방사관", "대뇌다리바닥", "대뇌다리"],
    "tr-cst-lateral": ["가쪽겉질척수로"],
    "tr-cst-anterior": ["앞겉질척수로"],
    "tr-corticobulbar": ["겉질핵로 (겉질숨뇌로)", "겉질핵로", "겉질숨뇌로", "속섬유막 무릎", "속섬유막", "대뇌다리바닥", "대뇌다리"],
    "tr-optic-radiation": ["시각부챗살", "속섬유막 뒤다리", "속섬유막"],
    "tr-cingulum": ["띠다발"],
    "tr-uncinate": ["갈고리다발"],
    "tr-arcuate": ["활꼴다발"],
}


def drop_covered(text, names):
    """remove the covered names from a '없음: A · B · 3D 없음: A, B' sentence, tidying separators; an
    empty list drops the whole sentence"""
    import re
    for n in sorted(names, key=len, reverse=True):
        text = re.sub(rf"(?<![가-힣]){re.escape(n)}(?![가-힣])", "", text)
    text = re.sub(r"\s*\(\s*\)", "", text)  # a name whose bracketed synonym was removed: '겉질핵로 ()'
    text = re.sub(r"(\s*[·,]\s*)+(?=\s*[·,]|\s*$|\s*3D 없음)", lambda m: " · " if "·" in m.group(0) else ", ", text)
    text = re.sub(r":\s*[·,]\s*", ": ", text)
    text = re.sub(r"\s*[·,]\s*(3D 없음)", r" · \1", text)
    text = re.sub(r"\s*[·,]\s*$", "", text).strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"·\s*3D 없음:\s*$", "", text).strip(" ·,")
    if re.fullmatch(r"(현재 제공 데이터에 독립 3D 정의 없음:?\s*)?(3D 없음:?\s*)?", text):
        return ""
    return text


def main(write):
    s = json.loads(STRUCTURES.read_text(encoding="utf-8"))
    by_id = {x["id"]: x for x in s["structures"]}
    anchor = max(i for i, x in enumerate(s["structures"]) if x["group"] == "tracts")
    for n in NEW_STRUCTURES:
        entry = {"id": n["id"], "group": "tracts", "tract": True, "name": n["name"],
                 "source": {"atlas": "hcp1065", "tracts": n["tracts"]}}
        if n.get("note"):
            entry["note"] = n["note"]
        if n["id"] in by_id:
            by_id[n["id"]].update(entry)
        else:
            anchor += 1
            s["structures"].insert(anchor, entry)
            by_id[n["id"]] = entry
    for sid, cl in CENTERLINE_FROM.items():
        by_id[sid]["source"]["centerlineFrom"] = cl
    p = json.loads(PATHWAYS.read_text(encoding="utf-8"))
    changed = []
    for pw in p["pathways"]:
        for st in pw["steps"]:
            hit = STEP_TRACTS.get(st["id"])
            if not hit:
                continue
            sid, side = hit
            if "missing" in st:
                cleaned = drop_covered(st["missing"]["ko"], COVERED_NAMES.get(sid, []))
                if cleaned:
                    st["missing"]["ko"] = cleaned
                else:
                    del st["missing"]
            if any(r["id"] == sid for r in st["structures"]):
                continue
            # the tract goes first so the route runs along it before reaching the step's grey matter
            st["structures"].insert(0, {"id": sid, "side": side})
            changed.append((pw["id"], st["id"], sid, side))
    print(f"structures: {len(NEW_STRUCTURES)} hcp1065 tracts, centerline overrides {list(CENTERLINE_FROM)}")
    print("pathway steps:", *changed, sep="\n  ")
    if write:
        STRUCTURES.write_text(json.dumps(s, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        PATHWAYS.write_text(json.dumps(p, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("written")


if __name__ == "__main__":
    main("--write" in sys.argv)
