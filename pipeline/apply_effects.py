#!/usr/bin/env python3
"""Body effects of pathway steps: which limb joint flexes (+deg) or extends (-deg) when the step is
reached (viewer: AtlasScene.setJointAngles), eye and pupil movements, and which of the step's muscles
relax instead of contracting (AtlasScene.setContractions). Schematic — the amounts are illustrative.

    pipeline/.venv/bin/python pipeline/apply_effects.py [--write]
"""
import sys

from atlas_pipeline.content import link_step, load_pathways, save_pathways

EFFECTS = {
    "corticospinal-lateral-4": [{"joint": "elbow", "side": "contra", "angle": 70}],
    "corticospinal-anterior-4": [{"joint": "shoulder", "side": "ipsi", "angle": 25}],
    "rubrospinal-3": [{"joint": "elbow", "side": "contra", "angle": 50}],
    "reticulospinal-medullary-3": [{"joint": "elbow", "side": "ipsi", "angle": 30}],
    "reticulospinal-pontine-3": [{"joint": "knee", "side": "ipsi", "angle": -8}, {"joint": "hip", "side": "ipsi", "angle": -8}],
    "vestibulospinal-lateral-3": [{"joint": "knee", "side": "ipsi", "angle": -8}, {"joint": "ankle", "side": "ipsi", "angle": -15}],
    "withdrawal-reflex-3": [{"joint": "hip", "side": "ipsi", "angle": 25}, {"joint": "knee", "side": "ipsi", "angle": 45}],
    "stretch-reflex-3": [{"joint": "knee", "side": "ipsi", "angle": -20}],
    "tectospinal-3": [],
}


# pupil effects (the iris ring scales): constrict for the light reflex and the near response, dilate for the sympathetic
PUPIL = {
    "pupillary-light-reflex-4": [{"pupil": "constrict", "side": "ipsi"}, {"pupil": "constrict", "side": "contra"}],
    "autonomic-pupil-dilation-3": [{"pupil": "dilate", "side": "ipsi"}],
    "accommodation-2": [{"pupil": "constrict", "side": "ipsi"}],
}


# eye movements (the globe with its parts turns about its centre) and lens accommodation
EYE = {
    "cranial-vi-motor-2": [{"eye": "abduct", "side": "ipsi", "angle": 25}],
    "cranial-iii-motor-2": [{"eye": "adduct", "side": "ipsi", "angle": 20}],
    "cranial-iv-motor-2": [{"eye": "depress", "side": "ipsi", "angle": 12}],
    "hvor-2": [{"eye": "abduct", "side": "contra", "angle": 20}],
    "hvor-4": [{"eye": "adduct", "side": "ipsi", "angle": 20}],
    "hvor-inhibition-2": [{"eye": "adduct", "side": "ipsi", "angle": 15}],
    "accommodation-3": [{"eye": "adduct", "side": "ipsi", "angle": 12}, {"eye": "adduct", "side": "contra", "angle": 12}],
    "accommodation-2": [{"lens": "accommodate", "side": "ipsi"}],
}


# muscles of a step that do not contract: an antagonist that relaxes (reciprocal inhibition) or a muscle whose
# stretch is only sensed. "*" means every muscle of the step; "relax" also shows it lengthening and dimmed
MUSCLE = {
    "withdrawal-reflex-3": [{"muscle": "mu-quadriceps", "side": "ipsi", "action": "relax"}],
    "stretch-reflex-1": [{"muscle": "*", "side": "ipsi", "action": "none"}],
    "hvor-inhibition-2": [{"muscle": "mu-lateral-rectus", "side": "ipsi", "action": "relax"}],
    "hvor-inhibition-3": [{"muscle": "mu-medial-rectus", "side": "contra", "action": "relax"}],
}


def main(write):
    p = load_pathways()
    n = 0
    for pw in p["pathways"]:
        for st in pw["steps"]:
            if st["id"] in EYE:
                st["effects"] = [e for e in st.get("effects", []) if "eye" not in e and "lens" not in e] + EYE[st["id"]]
                n += 1
            if st["id"] in PUPIL:
                st["effects"] = [e for e in st.get("effects", []) if "pupil" not in e] + PUPIL[st["id"]]
                link_step(p, st["id"], "so-iris", "ipsi")
                n += 1
            if st["id"] in EFFECTS:
                if EFFECTS[st["id"]]:
                    st["effects"] = EFFECTS[st["id"]]; n += 1
                else:
                    st.pop("effects", None)
            if st["id"] in MUSCLE:
                st["effects"] = [e for e in st.get("effects", []) if "muscle" not in e] + MUSCLE[st["id"]]
                for e in MUSCLE[st["id"]]:
                    if e["muscle"] != "*":
                        link_step(p, st["id"], e["muscle"], e["side"])
                n += 1
    print(f"{n} steps with effects")
    if write:
        save_pathways(p)
        print("written")


if __name__ == "__main__":
    main("--write" in sys.argv)
