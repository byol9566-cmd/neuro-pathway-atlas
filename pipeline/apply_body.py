#!/usr/bin/env python3
"""Whole-body structures from BodyParts3D (CC BY 4.0) as content entries: a ghost body (skin, skeleton
segments), the viscera and glands that autonomic pathways reach, and the skeletal muscles that motor
pathways end on. Names are BodyParts3D English part names (isa leaf names or part-of compound names);
left/right parts are real, not mirrored.

    pipeline/.venv/bin/python pipeline/apply_body.py [--write] [--allow-missing]

Exits non-zero when a part name is not in the BodyParts3D index, unless --allow-missing.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
from atlas_pipeline import bp3d  # noqa: E402
from atlas_pipeline.content import load_structures, save_structures, structure_index  # noqa: E402

GROUPS = {
    "body-shell": {"name": {"ko": "몸 외곽·뼈대", "en": "Body shell and skeleton"}, "color": "#9aa3ad"},
    "muscles": {"name": {"ko": "골격근", "en": "Skeletal muscles"}, "color": "#c4675a"},
    "viscera": {"name": {"ko": "내장·샘·혈관", "en": "Viscera, glands and vessels"}, "color": "#b98fd1"},
}


def lr(name_tpl):  # "{s} biceps brachii" -> {"R": [...], "L": [...]}
    return {"R": [name_tpl.format(s="right")], "L": [name_tpl.format(s="left")]}


def heads(side, *tpls):
    return [t.format(s=side) for t in tpls]


STRUCTURES_DEF = [
    # --- shell & skeleton (segments are kept separate so joints can be animated later)
    ("body-skin", "body-shell", {"ko": "피부 (몸 외곽)", "en": "Skin"}, {"M": ["skin"]}, 24000),
    ("bone-skull", "body-shell", {"ko": "머리뼈", "en": "Skull"}, {"M": ["skull", "mandible"]}, 8000),
    ("bone-vertebral-column", "body-shell", {"ko": "척주", "en": "Vertebral column"}, {"M": ["vertebral column", "sacrum"]}, 8000),
    ("bone-rib-cage", "body-shell", {"ko": "가슴우리", "en": "Rib cage"}, {"M": ["rib cage", "sternum"]}, 8000),
    ("bone-pelvis", "body-shell", {"ko": "골반", "en": "Pelvis"}, {"M": ["pelvis"]}, 5000),
    ("bone-shoulder", "body-shell", {"ko": "어깨뼈·빗장뼈", "en": "Scapula and clavicle"}, lr("{s} scapula") | {}, 3000),
    ("bone-humerus", "body-shell", {"ko": "위팔뼈", "en": "Humerus"}, lr("{s} humerus"), 2000),
    ("bone-forearm", "body-shell", {"ko": "아래팔뼈 (노뼈·자뼈)", "en": "Radius and ulna"}, {"R": ["right radius", "right ulna"], "L": ["left radius", "left ulna"]}, 2500),
    ("bone-hand", "body-shell", {"ko": "손", "en": "Hand"}, lr("{s} hand"), 3000),
    ("bone-femur", "body-shell", {"ko": "넙다리뼈·무릎뼈", "en": "Femur and patella"}, {"R": ["right femur", "right patella"], "L": ["left femur", "left patella"]}, 2500),
    ("bone-leg", "body-shell", {"ko": "종아리뼈 (정강뼈·종아리뼈)", "en": "Tibia and fibula"}, {"R": ["right tibia", "right fibula"], "L": ["left tibia", "left fibula"]}, 2500),
    ("bone-foot", "body-shell", {"ko": "발", "en": "Foot"}, lr("{s} foot"), 3000),
    # --- viscera, glands, vessels
    ("vs-heart", "viscera", {"ko": "심장", "en": "Heart"}, {"M": ["heart"]}, 6000),
    ("vs-lung", "viscera", {"ko": "허파", "en": "Lung"}, lr("{s} lung"), 6000),
    ("vs-trachea", "viscera", {"ko": "기관", "en": "Trachea"}, {"M": ["trachea"]}, 1500),
    ("vs-esophagus", "viscera", {"ko": "식도", "en": "Esophagus"}, {"M": ["esophagus"]}, 1500),
    ("vs-stomach", "viscera", {"ko": "위", "en": "Stomach"}, {"M": ["stomach"]}, 3000),
    ("vs-small-intestine", "viscera", {"ko": "작은창자", "en": "Small intestine"}, {"M": ["small intestine"]}, 8000),
    ("vs-large-intestine", "viscera", {"ko": "큰창자", "en": "Large intestine"}, {"M": ["large intestine"]}, 6000),
    ("vs-liver", "viscera", {"ko": "간", "en": "Liver"}, {"M": ["liver"]}, 5000),
    ("vs-gallbladder", "viscera", {"ko": "쓸개", "en": "Gallbladder"}, {"M": ["gallbladder"]}, 1000),
    ("vs-pancreas", "viscera", {"ko": "이자", "en": "Pancreas"}, {"M": ["pancreas"]}, 2000),
    ("vs-spleen", "viscera", {"ko": "지라", "en": "Spleen"}, {"M": ["spleen"]}, 2000),
    ("vs-kidney", "viscera", {"ko": "콩팥", "en": "Kidney"}, lr("{s} kidney"), 2500),
    ("vs-adrenal", "viscera", {"ko": "부신", "en": "Adrenal gland"}, lr("{s} adrenal gland"), 1500),
    ("vs-bladder", "viscera", {"ko": "방광", "en": "Urinary bladder"}, {"M": ["urinary bladder"]}, 1500),
    ("vs-prostate", "viscera", {"ko": "전립샘", "en": "Prostate"}, {"M": ["prostate"]}, 1000),
    ("vs-aorta", "viscera", {"ko": "대동맥", "en": "Aorta"}, {"M": ["aorta"]}, 4000),
    ("vs-carotid", "viscera", {"ko": "목동맥 (온·속목동맥)", "en": "Common and internal carotid artery"}, {"R": ["right common carotid artery", "right internal carotid artery"], "L": ["left common carotid artery", "left internal carotid artery"]}, 2500),
    ("vs-lacrimal-gland", "viscera", {"ko": "눈물샘", "en": "Lacrimal gland"}, lr("{s} lacrimal gland"), 800),
    ("vs-submandibular-gland", "viscera", {"ko": "턱밑샘", "en": "Submandibular gland"}, lr("{s} submandibular gland"), 1000),
    ("vs-sublingual-gland", "viscera", {"ko": "혀밑샘", "en": "Sublingual gland"}, lr("{s} sublingual gland"), 800),
    ("vs-tongue", "viscera", {"ko": "혀", "en": "Tongue"}, {"M": ["tongue"]}, 2500),
    ("vs-diaphragm", "viscera", {"ko": "가로막", "en": "Diaphragm"}, {"M": ["diaphragm"]}, 3000),
    # --- skeletal muscles (heads/parts summed into one muscle)
    ("mu-lateral-rectus", "muscles", {"ko": "가쪽곧은근", "en": "Lateral rectus"}, lr("{s} lateral rectus"), 1200),
    ("mu-medial-rectus", "muscles", {"ko": "안쪽곧은근", "en": "Medial rectus"}, lr("{s} medial rectus"), 1200),
    ("mu-superior-rectus", "muscles", {"ko": "위곧은근", "en": "Superior rectus"}, lr("{s} superior rectus"), 1200),
    ("mu-inferior-rectus", "muscles", {"ko": "아래곧은근", "en": "Inferior rectus"}, lr("{s} inferior rectus"), 1200),
    ("mu-superior-oblique", "muscles", {"ko": "위빗근", "en": "Superior oblique"}, lr("{s} superior oblique"), 1200),
    ("mu-inferior-oblique", "muscles", {"ko": "아래빗근", "en": "Inferior oblique"}, lr("{s} inferior oblique"), 1200),
    ("mu-levator-palpebrae", "muscles", {"ko": "위눈꺼풀올림근", "en": "Levator palpebrae superioris"}, lr("{s} levator palpebrae superioris"), 1000),
    ("mu-genioglossus", "muscles", {"ko": "턱끝혀근", "en": "Genioglossus"}, lr("{s} genioglossus"), 1000),
    ("mu-sternocleidomastoid", "muscles", {"ko": "목빗근", "en": "Sternocleidomastoid"}, lr("{s} sternocleidomastoid"), 1500),
    ("mu-trapezius", "muscles", {"ko": "등세모근", "en": "Trapezius"}, {s: heads(w, "descending part of {s} trapezius", "transverse part of {s} trapezius", "ascending part of {s} trapezius") for s, w in (("R", "right"), ("L", "left"))}, 2500),
    ("mu-deltoid", "muscles", {"ko": "어깨세모근", "en": "Deltoid"}, {s: heads(w, "clavicular part of {s} deltoid", "acromial part of {s} deltoid", "spinal part of {s} deltoid") for s, w in (("R", "right"), ("L", "left"))}, 2000),
    ("mu-pectoralis-major", "muscles", {"ko": "큰가슴근", "en": "Pectoralis major"}, lr("{s} pectoralis major"), 2000),
    ("mu-biceps-brachii", "muscles", {"ko": "위팔두갈래근", "en": "Biceps brachii"}, {s: heads(w, "long head of {s} biceps brachii", "short head of {s} biceps brachii") for s, w in (("R", "right"), ("L", "left"))}, 1500),
    ("mu-brachialis", "muscles", {"ko": "위팔근", "en": "Brachialis"}, lr("{s} brachialis"), 1000),
    ("mu-triceps-brachii", "muscles", {"ko": "위팔세갈래근", "en": "Triceps brachii"}, {s: heads(w, "long head of {s} triceps brachii", "lateral head of {s} triceps brachii", "medial head of {s} triceps brachii") for s, w in (("R", "right"), ("L", "left"))}, 2000),
    ("mu-iliopsoas", "muscles", {"ko": "엉덩허리근", "en": "Iliopsoas"}, {s: heads(w, "{s} psoas major", "{s} iliacus") for s, w in (("R", "right"), ("L", "left"))}, 2000),
    ("mu-gluteus-maximus", "muscles", {"ko": "큰볼기근", "en": "Gluteus maximus"}, lr("{s} gluteus maximus"), 2000),
    ("mu-quadriceps", "muscles", {"ko": "넙다리네갈래근", "en": "Quadriceps femoris"}, {s: heads(w, "{s} rectus femoris", "{s} vastus lateralis", "{s} vastus medialis", "{s} vastus intermedius") for s, w in (("R", "right"), ("L", "left"))}, 3000),
    ("mu-hamstrings", "muscles", {"ko": "넙다리뒤근육 (햄스트링)", "en": "Hamstrings"}, {s: heads(w, "long head of {s} biceps femoris", "short head of {s} biceps femoris", "{s} semitendinosus", "{s} semimembranosus") for s, w in (("R", "right"), ("L", "left"))}, 3000),
    ("mu-tibialis-anterior", "muscles", {"ko": "앞정강근", "en": "Tibialis anterior"}, lr("{s} tibialis anterior"), 1200),
    ("mu-triceps-surae", "muscles", {"ko": "종아리세갈래근 (장딴지근·가자미근)", "en": "Triceps surae"}, {s: heads(w, "medial head of {s} gastrocnemius", "lateral head of {s} gastrocnemius", "{s} soleus") for s, w in (("R", "right"), ("L", "left"))}, 2500),
]
# the right scapula/clavicle pair needs both names
for i, row in enumerate(STRUCTURES_DEF):
    if row[0] == "bone-shoulder":
        STRUCTURES_DEF[i] = (row[0], row[1], row[2], {"R": ["right scapula", "right clavicle"], "L": ["left scapula", "left clavicle"]}, row[4])
NOTE = "BodyParts3D(DBCLS, CC BY 4.0) 전신 모델의 저해상(99% 축소) 메시를 뇌·눈 랜드마크로 MNI에 맞춘 것. 개략 형태용 — 세부 모양은 믿지 말 것."


def main(write):
    data = load_structures()
    data["groups"].update({k: v for k, v in GROUPS.items() if k not in data["groups"]})
    by_id = structure_index(data)
    idx = bp3d.index()
    missing = []
    for sid, group, name, parts, budget in STRUCTURES_DEF:
        for side, names in parts.items():
            for n in names:
                if n not in idx:
                    missing.append((sid, n))
        entry = {"id": sid, "group": group, "name": name, "source": {"atlas": "bp3d", "parts": parts, "maxFaces": budget}, "note": NOTE}
        if sid in by_id:
            by_id[sid].update(entry)
        else:
            data["structures"].append(entry); by_id[sid] = entry
    print(f"{len(STRUCTURES_DEF)} body structures; missing part names: {missing}")
    if missing and "--allow-missing" not in sys.argv:
        # a renamed or absent part would silently drop out of its mesh (or fail the build): stop here
        sys.exit("BodyParts3D has no part with these names; fix STRUCTURES_DEF or pass --allow-missing")
    if write:
        save_structures(data)
        print("written")


if __name__ == "__main__":
    main("--write" in sys.argv)
