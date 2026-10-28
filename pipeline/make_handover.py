#!/usr/bin/env python3
"""Collect everything 성연 needs to review into one folder: docs/handover-seongyeon/review-<date>/,
plus review-<date>.zip next to it.

File and folder names are ASCII on purpose: a zip with Korean (NFD) names made on macOS showed up as
empty folders on Windows. The Korean titles stay inside the files.

    pipeline/.venv/bin/python pipeline/make_handover.py

Review sheets are regenerated from the same tables the pipeline uses, so an answer only has to name the
sheet, the row id and the correction.
"""
import csv
import datetime as dt
import importlib.util
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
HANDOVER = ROOT / "docs" / "handover-seongyeon"
TODAY = dt.date.today().isoformat()
OUT = HANDOVER / f"review-{TODAY}"
ZIP = HANDOVER / f"review-{TODAY}.zip"
MANIFEST = json.loads((ROOT / "viewer" / "public" / "data" / "manifest.json").read_text(encoding="utf-8"))
PATHWAYS = json.loads((ROOT / "content" / "pathways.json").read_text(encoding="utf-8"))["pathways"]
STRUCTURES = {s["id"]: s for s in json.loads((ROOT / "content" / "structures.json").read_text(encoding="utf-8"))["structures"]}
STEP = {st["id"]: (pw, st) for pw in PATHWAYS for st in pw["steps"]}


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "pipeline" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def ko(sid):
    s = STRUCTURES.get(sid)
    return s["name"]["ko"] if s else sid


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c).replace("|", "／").replace("\n", " ") for c in r) + " |" for r in rows]
    return "\n".join(out)


def sheet_effects():
    fx = load("apply_effects")
    rows = []
    for sid, lst in fx.EFFECTS.items():
        pw, st = STEP[sid]
        for e in lst:
            rows.append([sid, pw["name"]["ko"], st["title"]["ko"], f"{e['joint']} ({e['side']})", f"{e['angle']:+d}° ({'굽힘' if e['angle'] > 0 else '폄'})", ""])
    for sid, lst in fx.EYE.items():
        pw, st = STEP[sid]
        for e in lst:
            rows.append([sid, pw["name"]["ko"], st["title"]["ko"], f"눈 {e.get('eye') or e.get('lens')} ({e['side']})", f"{e.get('angle', '')}", ""])
    for sid, lst in fx.PUPIL.items():
        pw, st = STEP[sid]
        for e in lst:
            rows.append([sid, pw["name"]["ko"], st["title"]["ko"], f"동공 {e['pupil']} ({e['side']})", "", ""])
    for sid, lst in fx.MUSCLE.items():
        pw, st = STEP[sid]
        for e in lst:
            what = "근육 이완" if e["action"] == "relax" else "수축 없음" if e["action"] == "none" else "근육 수축"
            rows.append([sid, pw["name"]["ko"], st["title"]["ko"], f"{what} ({e['side']})", "모든 근육" if e["muscle"] == "*" else ko(e["muscle"]), ""])
    return "\n".join([
        "# 3. 경로 단계의 몸 작용 (관절·눈·동공·근육 이완)", "",
        "뷰어에서 그 단계에 도달하면 일어나는 움직임. 각도는 설명용 대표값. **틀린 것·빠진 것(어떤 경로의 마지막 단계에 어떤 관절·근육 작용이 있어야 하는지)**을 '답변' 열에 적어 주세요. 'ipsi/contra'는 경로의 기시쪽 기준.", "",
        md_table(["단계 id", "경로", "단계", "작용 (쪽)", "값", "답변"], rows), "",
        "## 단계 → 근육·장기 종착 (apply_body_targets.py)", "",
        md_table(["단계 id", "경로", "단계", "연결된 근육·장기", "답변"],
                 [[sid, STEP[sid][0]["name"]["ko"], STEP[sid][1]["title"]["ko"], ", ".join(f"{ko(s)} ({side})" for s, side in lst), ""]
                  for sid, lst in load("apply_body_targets").STEP_TARGETS.items() if lst and sid in STEP]),
    ])


def sheet_models():
    m = load("apply_models")
    rows = [[sid, ko(sid), v["shape"], v["centreMni"], v.get("axis", ""), json.dumps(v.get("params", {}), ensure_ascii=False), ""] for sid, v in m.MODELS.items()]
    return "\n".join([
        "# 5. 기하 모형 위치·치수 (속귀·신경절·목동맥)", "",
        "오른쪽 기준 MNI RAS(mm). `axis`는 모형의 긴 축/고리 법선이 향하는 방향. 치수는 교과서값. 위치가 수 mm 이상 틀리거나 방향이 반대면 적어 주세요.", "",
        md_table(["id", "이름", "모형", "중심 (x,y,z)", "축", "치수", "답변"], rows),
    ])


def sheet_autonomic():
    src = (ROOT / "pipeline" / "apply_autonomic.py").read_text(encoding="utf-8")
    rows = []
    for sid, s in STRUCTURES.items():
        if s["group"] == "peripheral" and s["source"].get("atlas") == "model" and sid.startswith("pn-") and sid in src:
            p = s["source"].get("params", {})
            pts = " → ".join(f"({x:g},{y:g},{z:g})" for x, y, z in p.get("points", [])) if "points" in p else f"타원체 {s['source'].get('centreMni')}"
            rows.append([sid, s["name"]["ko"], pts, s["source"].get("modelNote", "").split("관.")[-1].strip(), ""])
    seg = [[sid, ko(sid), f"z {STRUCTURES[sid]['source']['params']['z_top']} ~ {STRUCTURES[sid]['source']['params']['z_bottom']}", ""] for sid in STRUCTURES if sid.startswith("sp-seg-") or sid in ("sp-iml", "sp-clarke", "sp-sacral-parasympathetic")]
    return "\n".join([
        "# 4. 자율신경 말초 경유점과 척수 분절 범위", "",
        "경유점은 MNI RAS(mm), 오른쪽 기준. 몸은 BodyParts3D(성인 남성)에 뇌·눈 랜드마크로 맞춘 것이라 몸통 좌표는 '그 몸 안에서의 위치'로 보면 됩니다.", "",
        md_table(["id", "이름", "경유점", "교과서 주행", "답변"], rows), "",
        "## 척수 분절·기둥의 z 범위 (MNI mm; 큰구멍 ≈ −56, T1 척추뼈 ≈ −177, L1 ≈ −478)", "",
        md_table(["id", "이름", "범위", "답변"], seg),
    ])


# 검수시트2 file names -> ASCII (numeric prefix kept)
SHEET2_NAMES = {"0_안내.txt": "0_guide.txt", "2_경로.csv": "2_pathways.csv", "3_단계.csv": "3_steps.csv",
                "4_병변.csv": "4_lesions.csv", "6_판정.csv": "6_decisions.csv"}
SHOT_MAX_W = 1400
SHOT_MAX_KB = 400


def copy_sheet2(dst):
    dst.mkdir()
    for f in sorted((HANDOVER / "검수시트2").iterdir()):
        if f.is_file() and not f.name.startswith("."):
            name = SHEET2_NAMES.get(f.name)
            if name is None:  # unknown file: keep the numeric prefix, ascii-fy the rest
                prefix = f.name.split("_", 1)[0]
                name = f"{prefix}_file{f.suffix}" if prefix.isascii() else f"x_{abs(hash(f.name)) % 10**6}{f.suffix}"
                print("  note: unmapped 검수시트2 file", f.name, "->", name)
            shutil.copy2(f, dst / name)


def copy_screenshots(dst):
    """Latest 검수-*/7_뷰어_스크린샷 or review-*/7_viewer_screenshots -> dst, downscaled to <= 1400 px wide."""
    cands = sorted([d for d in HANDOVER.glob("검수-*/7_뷰어_스크린샷") if d.is_dir()]
                   + [d for d in HANDOVER.glob("review-*/7_viewer_screenshots") if d.is_dir() and d.parent != OUT],
                   key=lambda d: d.parent.name.split("-", 1)[1])
    if not cands:
        print("  no screenshot folder found; 7_viewer_screenshots/ skipped")
        return
    src = cands[-1]
    dst.mkdir()
    try:
        from PIL import Image
    except ImportError:
        Image = None
        print("  PIL not available: screenshots copied without resizing")
    for f in sorted(src.iterdir()):
        if not f.is_file() or f.name.startswith("."):
            continue
        out = dst / f.name
        if Image is not None and f.suffix.lower() == ".png":
            with Image.open(f) as im:
                im = im.convert("RGB")
                # palette PNG; if the noisy 3D render is still > SHOT_MAX_KB, step the width down
                for w in (SHOT_MAX_W, 1200, 1000, 800):
                    w = min(w, im.width)
                    x = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS) if w < im.width else im
                    x.quantize(colors=256, method=Image.Quantize.MEDIANCUT).save(out, optimize=True)
                    if out.stat().st_size <= SHOT_MAX_KB * 1024:
                        break
        else:
            shutil.copy2(f, out)


def write_zip():
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob("*")):
            arc = f"{OUT.name}/{p.relative_to(OUT).as_posix()}" + ("/" if p.is_dir() else "")
            assert arc.isascii(), f"non-ASCII name in zip: {arc}"
            if p.is_dir():
                z.writestr(arc, "")
            else:
                z.write(p, arc)


def status_numbers():
    """(steps that ride a real centreline, structures still placed as MNI ellipsoids, their Korean names)."""
    with_line = {m["structureId"] for m in MANIFEST["meshes"] if m.get("centerline")}
    n_line = sum(1 for pw in PATHWAYS for st in pw["steps"] if any(s["id"] in with_line for s in st["structures"]))
    mni = [s for s in STRUCTURES.values() if s.get("source", {}).get("atlas") == "mni"]
    return n_line, len(mni), "·".join(s["name"]["ko"] for s in mni)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    # 1. decisions and the 32-pathway drafts (existing sheets)
    copy_sheet2(OUT / "1_pathway_drafts_and_decisions")
    # 2. tract and nerve geometry sheets
    (OUT / "2a_tracts_cross_section_positions.md").write_text((ROOT / "docs/data/structures-3d/axis-tracts-review.md").read_text(encoding="utf-8"), encoding="utf-8")
    (OUT / "2b_cranial_nerve_waypoints.md").write_text((ROOT / "docs/data/structures-3d/cranial-nerves-review.md").read_text(encoding="utf-8"), encoding="utf-8")
    (OUT / "3_body_effects_joints_eyes_targets.md").write_text(sheet_effects() + "\n", encoding="utf-8")
    (OUT / "4_autonomic_waypoints_cord_segments.md").write_text(sheet_autonomic() + "\n", encoding="utf-8")
    (OUT / "5_parametric_models_inner_ear_ganglia.md").write_text(sheet_models() + "\n", encoding="utf-8")
    (OUT / "6_ref_brainstem_nuclei_coordinate_search.md").write_text((ROOT / "docs/data/structures-3d/coords-reticular-2026-10-05.md").read_text(encoding="utf-8"), encoding="utf-8")
    # answer template
    copy_screenshots(OUT / "7_viewer_screenshots")
    with (OUT / "ANSWERS.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["시트", "행 id", "판정(O/X)", "수정안", "근거(교과서·논문)"]); w.writerow(["예: 2a_tracts_cross_section_positions", "tr-rubrospinal", "X", "사람에선 C2 이하로 내려가지 않음 → z_bottom −120", "Nieuwenhuys 6판 p.xxx"])
    n_steps = sum(len(p["steps"]) for p in PATHWAYS)
    n_line, n_mni, mni_names = status_numbers()
    has_shots = (OUT / "7_viewer_screenshots").is_dir()
    shots_row = ("| 7 | `7_viewer_screenshots/` | 뷰어 화면 캡처(경로 재생·몸 보기) | 뷰어를 열기 어려울 때 참고 |\n" if has_shots else "")
    guide = f"""# 성연 검수 묶음 — {TODAY}

뷰어: https://neuro-pathway-atlas.vercel.app (경로 {len(PATHWAYS)}개, 구조 {len(STRUCTURES)}개). 아래 순서대로 보면 되고, **틀린 것만** `ANSWERS.csv`에 한 줄씩(시트 이름 · 행 id · O/X · 수정안 · 근거) 적어 주면 내가 표만 고쳐 다시 생성한다. 맞으면 안 적어도 됨.
`ANSWERS.csv`는 UTF-8(BOM 포함)이라 Excel에서 더블클릭으로 바로 열려도 한글이 깨지지 않는다. 저장할 때 형식은 그대로 CSV로.

| 순서 | 파일 | 내용 | 왜 필요한가 |
|---|---|---|---|
| 1 | `1_pathway_drafts_and_decisions/` | 경로 32개 설명 초안(2_pathways·3_steps·4_lesions csv, 안내는 0_guide.txt)과 **판정 시트 48건**(6_decisions.csv — 출처끼리 어긋나는 쟁점, 입장 중 고르기) | 판정이 와야 설명 문장을 확정해 뷰어 {len(PATHWAYS)}개 경로 설명 교체를 시작할 수 있음 (가장 급함) |
| 2 | `2a_tracts_cross_section_positions.md`, `2b_cranial_nerve_waypoints.md` | 아틀라스에 없어 교과서 단면 위치로 그린 척수·뇌줄기 섬유로 12개, 뇌신경 15개 경유점 | 뷰어 경로 재생 선이 이 위치를 따라감 |
| 3 | `3_body_effects_joints_eyes_targets.md` | 경로 마지막 단계의 관절 굽힘·폄, 안구 회전, 동공, 단계별 근육·장기 종착 | 팔다리·눈이 움직이는 연출의 근거 |
| 4 | `4_autonomic_waypoints_cord_segments.md` | 교감줄기·내장신경·골반내장신경 경유점, 척수 분절·IML·클라크기둥 z 범위 | 자율신경 경로 31개 |
| 5 | `5_parametric_models_inner_ear_ganglia.md` | 달팽이·반고리관·신경절·목동맥 모형의 위치·치수 | 근사 모형의 위치 확인 |
| 6 | `6_ref_brainstem_nuclei_coordinate_search.md` | RVLM·CVLM·거대세포핵·피개그물핵 좌표 문헌 조사 결과(참고) | 좌표가 실린 교과서·아틀라스(Olszewski & Baxter 1954 등)를 도서관에서 볼 수 있으면 알려 주기 |
{shots_row}
좌표계: 전부 MNI152 RAS(mm) — x 오른쪽+, y 앞+, z 위+; 앞맞교차 근처가 원점. 큰구멍 z≈−56, T1 척추뼈 z≈−177, L1 z≈−478.
뷰어에서 보는 법: 좌측 "구조" 목록에서 이름을 누르면 그 구조만 켜지고 카메라가 이동한다. "모형"/"근사" 꼬리표가 붙은 건 데이터가 아니라 모형. 경로는 "재생"으로 단계별 이동, 각 단계 상세에 어떤 구조·3D 없는 이름이 들어가는지 적혀 있다.
현황 숫자: 경로 단계 {n_steps}개 중 실제 주행선을 따르는 단계 {n_line}개, 근사 타원체로 남은 구조 {n_mni}개({mni_names}).
"""
    (OUT / "00_README_guide.md").write_text(guide, encoding="utf-8")
    write_zip()
    print("wrote", OUT, "and", ZIP.name, f"{ZIP.stat().st_size / 1024:.0f} KB")
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            print(" ", p.relative_to(OUT), f"{p.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
