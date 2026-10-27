#!/usr/bin/env python3
"""Turn the HCP1065 bundle centerlines (data/derived/tracts/centerlines.json, made by bundle_centerlines.py)
into the tract pieces the atlas uses: data/derived/tracts/tracts-prepared.json.

    pipeline/.venv/bin/python pipeline/tracts/prepare_tracts.py

Edits, each recorded in the output's `note`:
- cst-cerebral-{l,r}: the corticospinal bundle from the cortex down to the upper pons (z >= -22): corona
  radiata, posterior limb of the internal capsule, cerebral peduncle. The atlas bundle stops at the
  medulla and never crosses, so the medullary pyramid stays the NextBrain label.
- cst-lateral-{l,r}: the lateral corticospinal tract of that side of the cord, i.e. the continuation of the
  OTHER side's bundle after the pyramidal decussation: from the contralateral bundle's medullary end,
  across the midline over ~10 mm, then down the cord along the Visible Human cord axis
  (data/derived/vhp/sp-cord.M.mni-straight.nii.gz, re-posed by vhp_derive.py) offset posterolaterally into the lateral funiculus.
- cst-anterior-{l,r}: the uncrossed anterior corticospinal tract: the same side's bundle continued down the
  anterior funiculus next to the midline.
- ml-{l,r}: the atlas medial lemniscus runs on past the thalamus to the cortex (thalamocortical fibres);
  it is cut at the point nearest VPL.
- cbt, or, af, uf, cingulum (C_FPH): taken as they are. Radii are the bundle's median spread, clamped to
  1.5-6 mm so the tubes read as paths rather than volumes.
- icp-{l,r}, fornix-{l,r}: kept for centerline overrides of the NextBrain meshes.
Licence: HCP1065 is CC BY-SA 4.0 (https://brain.labsolver.org/hcp_trk_atlas.html); these derived paths carry
the same licence and attribution.
"""
import json
from pathlib import Path

import numpy as np
import nibabel as nib

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "derived" / "tracts" / "centerlines.json"
CORD = ROOT / "data" / "derived" / "vhp" / "sp-cord.M.mni-straight.nii.gz"  # vhp_derive.py
OUT = ROOT / "data" / "derived" / "tracts" / "tracts-prepared.json"
VPL = {"l": np.array([-15.0, -20.0, 5.0]), "r": np.array([15.0, -20.0, 5.0])}
CORD_BOTTOM = -230.0


def clamp(radii, lo=1.5, hi=6.0):
    return [float(min(hi, max(lo, r))) for r in radii]


def cord_axis():
    """z -> (x, y, radius) of the Visible Human cord in MNI, sampled every mm"""
    img = nib.as_closest_canonical(nib.load(CORD))
    a = np.asanyarray(img.dataobj) > 0
    A = img.affine
    out = {}
    for k in range(a.shape[2]):
        sl = a[:, :, k]
        if sl.sum() < 20:
            continue
        ii, jj = np.nonzero(sl)
        c = A @ np.array([ii.mean(), jj.mean(), k, 1.0])
        out[round(float(c[2]))] = (float(c[0]), float(c[1]), float(np.sqrt(sl.sum() / np.pi) * abs(A[0, 0])))
    return out


def smooth_z(axis):
    """the per-slice centroids wobble by a millimetre; a running mean over 15 mm steadies the funiculus path"""
    zs = sorted(axis)
    xs = np.array([axis[z][0] for z in zs]); ys = np.array([axis[z][1] for z in zs]); rs = np.array([axis[z][2] for z in zs])
    k = np.ones(15) / 15
    pad = lambda v: np.convolve(np.pad(v, 7, mode="edge"), k, mode="valid")
    return {z: (float(x), float(y), float(r)) for z, x, y, r in zip(zs, pad(xs), pad(ys), pad(rs))}


def cord_run(axis, z_top, z_bottom, offset_fn, step=4.0):
    pts = []
    z = z_top
    zs = sorted(axis)
    while z >= z_bottom:
        zn = min(zs, key=lambda v: abs(v - z))
        cx, cy, r = axis[zn]
        dx, dy = offset_fn(r)
        pts.append([cx + dx, cy + dy, float(z)])
        z -= step
    return pts


def blend(a, b, n):
    """n points on a smooth S-curve from a to b (cosine ease), excluding a"""
    out = []
    for i in range(1, n + 1):
        t = i / n
        s = (1 - np.cos(np.pi * t)) / 2
        out.append(list(np.array(a) * (1 - s) + np.array(b) * s))
    return out


def main():
    data = json.loads(SRC.read_text())
    by_id = {t["id"]: t for t in data["tracts"]}
    axis = smooth_z(cord_axis())
    top = max(axis)
    prepared = {}

    def put(pid, points, radii, note, source):
        pts = [[round(float(v), 2) for v in p] for p in points]
        prepared[pid] = {"points": pts, "radiiMm": [round(r, 2) for r in radii], "note": note, "atlasBundles": source}

    for side in ("l", "r"):
        cst = by_id[f"cst-{side}"]
        P = np.array(cst["points"]); R = np.array(cst["radiiMm"])
        keep = P[:, 2] >= -22
        put(f"cst-cerebral-{side}", P[keep], clamp(R[keep]), "HCP1065 겉질척수 다발의 겉질~위다리뇌 구간(z ≥ −22). 숨뇌 피라미드는 NextBrain 라벨.", [cst["atlasName"]])

        # lateral CST on this side = other side's bundle after the decussation
        other = by_id[f"cst-{'r' if side == 'l' else 'l'}"]
        end = np.array(other["points"][-1])  # medullary end, x on the other side
        sign = -1.0 if side == "l" else 1.0
        lateral = lambda r, s=sign: (s * 0.55 * r, -0.35 * r)  # posterolateral: the lateral funiculus
        cx, cy, r0 = axis[top]
        cross_to = np.array([cx + lateral(r0)[0], cy + lateral(r0)[1], float(top) - 2.0])
        pts = [list(end)] + blend(end, cross_to, 4) + cord_run(axis, top - 6.0, CORD_BOTTOM, lateral)
        put(f"cst-lateral-{side}", pts, [2.5] * len(pts),
            "피라미드교차는 반대쪽 HCP1065 다발의 숨뇌 끝에서 그렸고, 그 아래는 Visible Human 척수(자세 보정)의 가쪽기둥을 따른다. 교차와 기둥 위치는 교과서 기하이지 아틀라스 데이터가 아니다.",
            [other["atlasName"], "VHP spinal cord"])

        # anterior CST: same side, anterior funiculus by the midline
        same_end = np.array(cst["points"][-1])
        anterior = lambda r, s=sign: (s * 0.2 * r, 0.6 * r)
        cross_to = np.array([cx + anterior(r0)[0], cy + anterior(r0)[1], float(top) - 2.0])
        pts = [list(same_end)] + blend(same_end, cross_to, 4) + cord_run(axis, top - 6.0, -150.0, anterior)
        put(f"cst-anterior-{side}", pts, [1.8] * len(pts),
            "교차하지 않은 같은 쪽 HCP1065 다발을 Visible Human 척수 앞기둥을 따라 T1 부근까지 이었다. 기둥 위치는 교과서 기하.",
            [cst["atlasName"], "VHP spinal cord"])

        ml = by_id[f"ml-{side}"]
        P = np.array(ml["points"]); R = np.array(ml["radiiMm"])
        k = int(np.argmin(np.linalg.norm(P - VPL[side], axis=1)))
        put(f"ml-{side}", P[: k + 1], clamp(R[: k + 1]), f"HCP1065 안쪽섬유띠 다발을 VPL에 가장 가까운 점 {P[k].round(1).tolist()}에서 잘랐다(아틀라스 다발은 겉질까지 이어진다).", [ml["atlasName"]])

        for pid, src in (("cbt", f"cbt-{side}"), ("or", f"or-{side}"), ("af", f"af-{side}"), ("uf", f"uf-{side}"), ("cingulum", f"c-fph-{side}"), ("icp", f"icp-{side}"), ("fornix", f"f-{side}"),
                         ("tr-s", f"tr-s-{side}"), ("tr-a", f"tr-a-{side}"), ("tr-p", f"tr-p-{side}"), ("ar", f"ar-{side}"),
                         ("cs-a", f"cs-a-{side}"), ("cs-p", f"cs-p-{side}"), ("cs-s", f"cs-s-{side}"),
                         ("slf1", f"slf1-{side}"), ("slf2", f"slf2-{side}"), ("slf3", f"slf3-{side}"), ("ifof", f"ifof-{side}"), ("ilf", f"ilf-{side}"),
                         ("mdlf", f"mdlf-{side}"), ("emc", f"emc-{side}"), ("fat", f"fat-{side}"), ("vof", f"vof-{side}"), ("pat", f"pat-{side}")):
            t = by_id[src]
            put(f"{pid}-{side}", t["points"], clamp(t["radiiMm"]), "HCP1065 다발 중심선 그대로(반지름은 다발 퍼짐의 중앙값, 1.5~6 mm로 제한).", [t["atlasName"]])

        # dentatorubrothalamic: the atlas bundle stays on one side (tractography does not resolve the
        # decussation of the superior cerebellar peduncle), so the thalamocortical part is mirrored to the
        # other hemisphere and the two halves are joined across the midline in the caudal midbrain
        drtt = by_id[f"drtt-{side}"]
        P = np.array(drtt["points"]); R = clamp(drtt["radiiMm"])
        if P[0, 2] < P[-1, 2]:  # order cortex -> cerebellum
            P = P[::-1]; R = R[::-1]
        z_hi, z_lo = -10.0, -22.0  # decussation band
        w = np.clip((P[:, 2] - z_lo) / (z_hi - z_lo), 0, 1)  # 1 above the band (mirror), 0 below (keep)
        s = (1 - np.cos(np.pi * w)) / 2
        Q = P.copy(); Q[:, 0] = P[:, 0] * (1 - 2 * s)
        put(f"drtt-crossed-{side}", Q, R, "치아핵에서 시작하는 쪽 기준: 소뇌 부분은 HCP1065 치아핵적색시상로(DRTT) 그대로, 위소뇌다리 교차(z −22~−10)에서 정중선을 건너 반대쪽 시상·겉질 부분은 같은 다발을 좌우 반전해 이었다. 아틀라스 다발은 교차하지 않는다.", [drtt["atlasName"]])

    cc = by_id["cc"]
    put("cc", cc["points"], clamp(cc["radiiMm"]), "HCP1065 뇌량 전체 다발의 대표 중심선(몸통을 지나는 하나의 선). 부위별(무릎·몸통·팽대) 섬유는 구분하지 않았다.", [cc["atlasName"]])

    OUT.write_text(json.dumps({"source": data["source"], "tracts": prepared}, ensure_ascii=False, indent=1) + "\n")
    for pid, t in prepared.items():
        p = np.array(t["points"])
        print(f"{pid:18s} n={len(p):3d} start={p[0].round(0).tolist()} end={p[-1].round(0).tolist()}")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
