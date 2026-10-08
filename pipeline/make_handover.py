#!/usr/bin/env python3
"""Collect everything 성연 needs to review into one folder: docs/handover-seongyeon/검수-<date>/.

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
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
OUT = ROOT / "docs" / "handover-seongyeon" / f"검수-{dt.date.today().isoformat()}"
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
    return "\n".join([
        "# 3. 경로 단계의 몸 작용 (관절·눈·동공)", "",
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


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    # 1. decisions and the 32-pathway drafts (existing sheets)
    shutil.copytree(ROOT / "docs" / "handover-seongyeon" / "검수시트2", OUT / "1_경로설명_초안과_판정시트")
    # 2. tract and nerve geometry sheets
    (OUT / "2_섬유로_단면위치.md").write_text((ROOT / "docs/data/structures-3d/axis-tracts-review.md").read_text(encoding="utf-8"), encoding="utf-8")
    (OUT / "2_뇌신경_경유점.md").write_text((ROOT / "docs/data/structures-3d/cranial-nerves-review.md").read_text(encoding="utf-8"), encoding="utf-8")
    (OUT / "3_몸작용_관절_눈_종착.md").write_text(sheet_effects() + "\n", encoding="utf-8")
    (OUT / "4_자율신경_경유점_척수분절.md").write_text(sheet_autonomic() + "\n", encoding="utf-8")
    (OUT / "5_기하모형_속귀_신경절.md").write_text(sheet_models() + "\n", encoding="utf-8")
    (OUT / "6_참고_뇌줄기핵_좌표조사.md").write_text((ROOT / "docs/data/structures-3d/coords-reticular-2026-10-05.md").read_text(encoding="utf-8"), encoding="utf-8")
    # answer template
    with (OUT / "답변.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["시트", "행 id", "판정(O/X)", "수정안", "근거(교과서·논문)"]); w.writerow(["예: 2_섬유로_단면위치", "tr-rubrospinal", "X", "사람에선 C2 이하로 내려가지 않음 → z_bottom −120", "Nieuwenhuys 6판 p.xxx"])
    n_steps = sum(len(p["steps"]) for p in PATHWAYS)
    guide = f"""# 성연 검수 묶음 — {dt.date.today().isoformat()}

뷰어: https://neuro-pathway-atlas.vercel.app (경로 247개, 구조 {len(STRUCTURES)}개). 아래 순서대로 보면 되고, **틀린 것만** `답변.csv`에 한 줄씩(시트 이름 · 행 id · O/X · 수정안 · 근거) 적어 주면 내가 표만 고쳐 다시 생성한다. 맞으면 안 적어도 됨.

| 순서 | 파일 | 내용 | 왜 필요한가 |
|---|---|---|---|
| 1 | `1_경로설명_초안과_판정시트/` | 경로 32개 설명 초안(2_경로·3_단계·4_병변 csv)과 **판정 시트 48건**(6_판정.csv — 출처끼리 어긋나는 쟁점, 입장 중 고르기) | 판정이 와야 설명 문장을 확정해 뷰어 247개 경로 설명 교체를 시작할 수 있음 (가장 급함) |
| 2 | `2_섬유로_단면위치.md`, `2_뇌신경_경유점.md` | 아틀라스에 없어 교과서 단면 위치로 그린 척수·뇌줄기 섬유로 12개, 뇌신경 15개 경유점 | 뷰어 경로 재생 선이 이 위치를 따라감 |
| 3 | `3_몸작용_관절_눈_종착.md` | 경로 마지막 단계의 관절 굽힘·폄, 안구 회전, 동공, 단계별 근육·장기 종착 | 팔다리·눈이 움직이는 연출의 근거 |
| 4 | `4_자율신경_경유점_척수분절.md` | 교감줄기·내장신경·골반내장신경 경유점, 척수 분절·IML·클라크기둥 z 범위 | 자율신경 경로 31개 |
| 5 | `5_기하모형_속귀_신경절.md` | 달팽이·반고리관·신경절·목동맥 모형의 위치·치수 | 근사 모형의 위치 확인 |
| 6 | `6_참고_뇌줄기핵_좌표조사.md` | RVLM·CVLM·거대세포핵·피개그물핵 좌표 문헌 조사 결과(참고) | 좌표가 실린 교과서·아틀라스(Olszewski & Baxter 1954 등)를 도서관에서 볼 수 있으면 알려 주기 |

좌표계: 전부 MNI152 RAS(mm) — x 오른쪽+, y 앞+, z 위+; 앞맞교차 근처가 원점. 큰구멍 z≈−56, T1 척추뼈 z≈−177, L1 z≈−478.
뷰어에서 보는 법: 좌측 "구조" 목록에서 이름을 누르면 그 구조만 켜지고 카메라가 이동한다. "모형"/"근사" 꼬리표가 붙은 건 데이터가 아니라 모형. 경로는 "재생"으로 단계별 이동, 각 단계 상세에 어떤 구조·3D 없는 이름이 들어가는지 적혀 있다.
현황 숫자: 경로 단계 {n_steps}개 중 실제 주행선을 따르는 단계 140개 이상, 근사 타원체로 남은 구조 4개(RVLM·CVLM·거대세포핵·피개그물핵).
"""
    (OUT / "0_안내.md").write_text(guide, encoding="utf-8")
    print("wrote", OUT)
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            print(" ", p.relative_to(OUT), f"{p.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
