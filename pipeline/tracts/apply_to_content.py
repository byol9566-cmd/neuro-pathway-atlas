#!/usr/bin/env python3
"""Register the prepared HCP1065 tracts in content/: new tract structures, centerline overrides for the
NextBrain tract labels, and the pathway steps that should follow them.

    pipeline/.venv/bin/python pipeline/tracts/apply_to_content.py [--write]

Idempotent: structures already present are updated in place, pathway steps get a tract only once.
Which steps get which tract is an explicit table below (the steps' `missing` text names the tract), not a
keyword match — '활꼴' also matches the arcuate *nucleus*.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))
from atlas_pipeline.content import (insert_after_group, link_step, load_pathways, load_structures,  # noqa: E402
                                    save_pathways, save_structures, structure_index)

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
    {"id": "tr-thalamic-radiation-superior", "name": {"ko": "위시상부챗살 (VPL·VL → 중심앞·뒤이랑)", "en": "Superior thalamic radiation"}, "tracts": {"L": "tr-s-l", "R": "tr-s-r"}},
    {"id": "tr-thalamic-radiation-anterior", "name": {"ko": "앞시상부챗살 (MD·VA → 전전두)", "en": "Anterior thalamic radiation"}, "tracts": {"L": "tr-a-l", "R": "tr-a-r"}},
    {"id": "tr-thalamic-radiation-posterior", "name": {"ko": "뒤시상부챗살 (베개 → 마루·뒤통수)", "en": "Posterior thalamic radiation"}, "tracts": {"L": "tr-p-l", "R": "tr-p-r"}},
    {"id": "tr-acoustic-radiation", "name": {"ko": "청각부챗살", "en": "Acoustic radiation"}, "tracts": {"L": "ar-l", "R": "ar-r"}},
    {"id": "tr-corticostriatal-superior", "name": {"ko": "겉질선조체섬유 (운동·감각겉질 → 조가비핵)", "en": "Corticostriatal tract, superior"}, "tracts": {"L": "cs-s-l", "R": "cs-s-r"}},
    {"id": "tr-corticostriatal-anterior", "name": {"ko": "겉질선조체섬유 (전전두 → 꼬리핵)", "en": "Corticostriatal tract, anterior"}, "tracts": {"L": "cs-a-l", "R": "cs-a-r"}},
    {"id": "tr-corticostriatal-posterior", "name": {"ko": "겉질선조체섬유 (마루·뒤통수 → 선조체)", "en": "Corticostriatal tract, posterior"}, "tracts": {"L": "cs-p-l", "R": "cs-p-r"}},
    {"id": "tr-drtt", "name": {"ko": "치아핵적색시상로", "en": "Dentatorubrothalamic tract"}, "tracts": {"L": "drtt-crossed-l", "R": "drtt-crossed-r"},
     "note": "좌/우는 치아핵이 있는 쪽. 교차는 교과서 기하로 구성(아틀라스 다발은 교차하지 않음)."},
    {"id": "tr-slf-1", "name": {"ko": "위세로다발 I", "en": "Superior longitudinal fasciculus I"}, "tracts": {"L": "slf1-l", "R": "slf1-r"}},
    {"id": "tr-slf-2", "name": {"ko": "위세로다발 II", "en": "Superior longitudinal fasciculus II"}, "tracts": {"L": "slf2-l", "R": "slf2-r"}},
    {"id": "tr-slf-3", "name": {"ko": "위세로다발 III", "en": "Superior longitudinal fasciculus III"}, "tracts": {"L": "slf3-l", "R": "slf3-r"}},
    {"id": "tr-ifof", "name": {"ko": "아래이마뒤통수다발", "en": "Inferior fronto-occipital fasciculus"}, "tracts": {"L": "ifof-l", "R": "ifof-r"}},
    {"id": "tr-ilf", "name": {"ko": "아래세로다발", "en": "Inferior longitudinal fasciculus"}, "tracts": {"L": "ilf-l", "R": "ilf-r"}},
    {"id": "tr-mdlf", "name": {"ko": "중간세로다발", "en": "Middle longitudinal fasciculus"}, "tracts": {"L": "mdlf-l", "R": "mdlf-r"}},
    {"id": "tr-extreme-capsule", "name": {"ko": "극섬유막", "en": "Extreme capsule"}, "tracts": {"L": "emc-l", "R": "emc-r"}},
    {"id": "tr-fat", "name": {"ko": "이마빗다발 (FAT)", "en": "Frontal aslant tract"}, "tracts": {"L": "fat-l", "R": "fat-r"}},
    {"id": "tr-vof", "name": {"ko": "뒤통수세로다발 (VOF)", "en": "Vertical occipital fasciculus"}, "tracts": {"L": "vof-l", "R": "vof-r"}},
    {"id": "tr-pat", "name": {"ko": "마루빗다발 (PAT)", "en": "Parietal aslant tract"}, "tracts": {"L": "pat-l", "R": "pat-r"}},
    {"id": "tr-corpus-callosum", "name": {"ko": "뇌들보 (뇌량)", "en": "Corpus callosum"}, "tracts": {"M": "cc"}},
]
CENTERLINE_FROM = {
    "tr-medial-lemniscus": {"L": "ml-l", "R": "ml-r"},
    "tr-icp": {"L": "icp-l", "R": "icp-r"},
    "tr-fornix": {"L": "fornix-l", "R": "fornix-r"},
}
# step id -> [(structure id, side), ...]. The side follows the structure the step already names.
STEP_TRACTS = {
    "dcml-5": [("tr-thalamic-radiation-superior", "contra")],
    "spinothalamic-lateral-3": [("tr-thalamic-radiation-superior", "contra")],
    "spinothalamic-anterior-3": [("tr-thalamic-radiation-superior", "contra")],
    "trigeminal-touch-3": [("tr-thalamic-radiation-superior", "contra")],
    "trigeminal-pain-3": [("tr-thalamic-radiation-superior", "contra")],
    "somatosensory-cortical-processing-1": [("tr-thalamic-radiation-superior", "contra")],
    "thalamocortical-oscillation-1": [("tr-thalamic-radiation-superior", "ipsi")],
    "basal-ganglia-indirect-6": [("tr-thalamic-radiation-superior", "ipsi")],
    "basal-ganglia-direct-5": [("tr-thalamic-radiation-superior", "ipsi")],
    "stn-dbs-network-2": [("tr-thalamic-radiation-superior", "ipsi")],
    "nigrostriatal-3": [("tr-thalamic-radiation-superior", "ipsi")],
    "dentatothalamocortical-3": [("tr-thalamic-radiation-superior", "contra")],
    "cerebellar-double-crossing-1": [("tr-drtt", "ipsi"), ("tr-thalamic-radiation-superior", "contra")],
    "dentatothalamocortical-2": [("tr-drtt", "ipsi")],
    "auditory-central-5": [("tr-acoustic-radiation", "ipsi")],
    "auditory-itd-3": [("tr-acoustic-radiation", "ipsi")],
    "auditory-tonotopy-3": [("tr-acoustic-radiation", "ipsi")],
    "basal-ganglia-direct-2": [("tr-corticostriatal-superior", "ipsi")],
    "basal-ganglia-indirect-2": [("tr-corticostriatal-superior", "ipsi")],
    "procedural-memory-2": [("tr-corticostriatal-superior", "ipsi")],
    "caudate-motivation-1": [("tr-corticostriatal-anterior", "ipsi")],
    "association-longitudinal-2": [("tr-slf-2", "ipsi"), ("tr-ifof", "ipsi"), ("tr-ilf", "ipsi")],
    "parietal-prefrontal-information-2": [("tr-slf-2", "ipsi")],
    "working-memory-2": [("tr-slf-2", "ipsi")],
    "language-ventral-2": [("tr-ifof", "ipsi")],
    "visual-ventral-3": [("tr-ilf", "ipsi")],
    "commissural-connections-1": [("tr-corpus-callosum", "ipsi")],
    "split-brain-language-2": [("tr-corpus-callosum", "ipsi")],
    "corticospinal-lateral-1": [("tr-cst-cerebral", "ipsi")],
    "corticospinal-lateral-3": [("tr-cst-lateral", "contra")],
    "corticospinal-anterior-1": [("tr-cst-cerebral", "ipsi")],
    "corticospinal-anterior-3": [("tr-cst-anterior", "ipsi")],
    "cerebellar-double-crossing-2": [("tr-cst-lateral", "contra")],
    "corticobulbar-1": [("tr-corticobulbar", "ipsi")],
    "language-spoken-4": [("tr-corticobulbar", "ipsi")],
    "language-written-4": [("tr-corticobulbar", "ipsi")],
    "visual-temporal-3": [("tr-optic-radiation", "ipsi")],
    "visual-nasal-3": [("tr-optic-radiation", "contra")],
    "papez-5": [("tr-cingulum", "ipsi")],
    "association-cingulum-2": [("tr-cingulum", "ipsi")],
    "association-uncinate-2": [("tr-uncinate", "ipsi")],
    "language-spoken-3": [("tr-arcuate", "ipsi")],
    "language-dorsal-2": [("tr-arcuate", "ipsi")],
    "language-written-3": [("tr-arcuate", "ipsi")],
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
    "tr-thalamic-radiation-superior": ["속섬유막 뒤다리", "속섬유막", "방사관"],
    "tr-acoustic-radiation": ["청각부챗살", "속섬유막 렌즈핵밑부분", "속섬유막"],
    "tr-slf-2": ["위세로다발"],
    "tr-ilf": ["아래세로다발"],
    "tr-ifof": ["아래이마뒤통수다발"],
    "tr-corpus-callosum": ["뇌들보"],
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
    s = load_structures()
    by_id = structure_index(s)
    for n in NEW_STRUCTURES:
        entry = {"id": n["id"], "group": "tracts", "tract": True, "name": n["name"],
                 "source": {"atlas": "hcp1065", "tracts": n["tracts"]}}
        if n.get("note"):
            entry["note"] = n["note"]
        if n["id"] in by_id:
            by_id[n["id"]].update(entry)
        else:
            insert_after_group(s["structures"], "tracts", entry)
            by_id[n["id"]] = entry
    for sid, cl in CENTERLINE_FROM.items():
        by_id[sid]["source"]["centerlineFrom"] = cl
    p = load_pathways()
    changed = []
    for pw in p["pathways"]:
        for st in pw["steps"]:
            for sid, side in STEP_TRACTS.get(st["id"], []):
                if "missing" in st:
                    cleaned = drop_covered(st["missing"]["ko"], COVERED_NAMES.get(sid, []))
                    if cleaned:
                        st["missing"]["ko"] = cleaned
                    else:
                        del st["missing"]
                # the tract goes first so the route runs along it before reaching the step's grey matter
                if link_step(p, st["id"], sid, side, "front"):
                    changed.append((pw["id"], st["id"], sid, side))
    print(f"structures: {len(NEW_STRUCTURES)} hcp1065 tracts, centerline overrides {list(CENTERLINE_FROM)}")
    print("pathway steps:", *changed, sep="\n  ")
    if write:
        save_structures(s)
        save_pathways(p)
        print("written")


if __name__ == "__main__":
    main("--write" in sys.argv)
