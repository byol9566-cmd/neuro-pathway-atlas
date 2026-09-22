#!/usr/bin/env python3
"""Turn the verified wanted/*.json files into WANTED.md: what the owner should fetch from the library."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
# pathways whose current evidence REVIEW.md flagged ⚠️ (single StatPearls chapter, source error, contradiction, case report)
PRIORITY = {"trigeminal-somatosensory-pathways", "descending-pain-modulation", "basal-ganglia-circuits", "cerebellar-circuits",
            "corneal-blink-reflex", "amygdala-fear-circuit", "gustatory-pathway", "sympathetic-pathway-to-the-eye-horner-syndrome",
            "horizontal-vestibulo-ocular-reflex", "hypothalamo-pituitary-axes", "anterolateral-system-spinothalamic-tract", "corticospinal-tracts"}
ANIMAL = {"10.1002/cne.901460102", "10.1093/brain/91.1.1", "10.1212/wnl.37.6.930"}  # Moore & Lenn (rat), Lawrence & Kuypers (monkey), Jenny & Saper (monkey)
NOTES = {
    "9783805522106": "❓ 이 ISBN은 1981년 2판. 3판(2014, Büttner-Ennever & Horn 편)이 있으면 그쪽이 낫습니다.",
    "9781416047056": "2011년판. 후속판(Fitzgerald's Clinical Neuroanatomy and Neuroscience, 7·8판)이면 어느 판이든 됩니다.",
    "9781597565308": "❓ ISBN을 Open Library에서 확인 못 함(Plural Publishing). 도서관 검색은 제목으로.",
}

books, articles = {}, {}
for f in [HERE / a for a in sys.argv[1:]]:
    data = json.loads(f.read_text(encoding="utf-8"))
    report = json.loads(f.with_suffix(".report.json").read_text(encoding="utf-8"))
    rep = {(b["batch"], p["id"], i): c for b in report["batches"] for p in b["pathways"] for i, c in enumerate(p["candidates"])}
    for b in data["batches"]:
        for p in b["pathways"]:
            for i, c in enumerate(p["candidates"]):
                r = rep.get((b["batch"], p["id"], i), {})
                if r.get("status") not in ("OK", "NO_DOI") and not (c.get("kind") == "book" and r.get("status") == "ISBN_NOT_FOUND"):
                    continue
                if c.get("kind") == "book":
                    key = (c.get("isbn") or c["citation"]).split()[0]
                    row = books.setdefault(key, {"c": c, "uses": [], "chapters": []})
                    row["uses"].append(p["id"])
                    if c.get("chapter") and c["chapter"] not in row["chapters"]:
                        row["chapters"].append(c["chapter"])
                else:
                    key = c.get("doi") or c["citation"]
                    epmc = r.get("epmc") or {}
                    row = articles.setdefault(key, {"c": c, "uses": [], "free": bool(epmc.get("pmcid") or epmc.get("isOpenAccess") == "Y"), "pmcid": epmc.get("pmcid")})
                    row["uses"].append(p["id"])

def cell(s):
    return (s or "").replace("|", "/").replace("\n", " ")

out = ["# 도서관에서 받아 주실 문헌 목록 (WANTED)", "",
       "근거 데이터의 StatPearls(B등급) 의존을 A등급 문헌으로 바꾸기 위한 목록입니다. 후보는 서브에이전트 3개가 찾고, 모든 DOI·ISBN은 메인 세션이 Crossref·Europe PMC·Open Library로 다시 확인했습니다(`verify_wanted.py`, 결과는 `*.report.json`). 전문을 열어 내용까지 확인한 것은 아직 없습니다 — 받아 주시면 그때 인용문을 뽑고 `verify_quotes.py`로 검증합니다.", "",
       "**받는 방법**: PDF를 `~/Downloads/atlas-refs/` 에 넣어 주세요. 파일명은 자유(첫 저자·연도 정도). 전자책은 필요한 장만 PDF로 저장해도 됩니다.", "",
       "**순서 제안**: ① 교과서 4권(아래 A의 ★) → ② 1순위 논문 → ③ 나머지. 교과서 4권만 있어도 경로 대부분의 기본 사슬(뉴런 차수·교차·시냅스 핵)은 A급으로 받칠 수 있어서, 시간이 없으면 ①②까지만 해도 됩니다.", ""]

out += ["## A. 교과서·단행본 (도서관 전자책)", "", "| 받기 | 책 | ISBN | 필요한 장 | 쓰이는 경로 | 비고 |", "|---|---|---|---|---|---|"]
core = {"9783540346845", "9780323396325", "9780190228958", "9781259642234"}
for key, row in sorted(books.items(), key=lambda kv: (kv[0] not in core, kv[1]["c"]["citation"])):
    c = row["c"]
    star = "★" if key in core else ""
    uses = ", ".join(dict.fromkeys(row["uses"]))
    out.append(f"| ✅{star} | {cell(c['citation'])} | {key} | {cell('; '.join(row['chapters']))} | {uses} | {NOTES.get(key, '')} |")
out.append("")

out += ["## B. 논문", "", "🆓 = PMC/오픈액세스에 전문이 있어 제가 직접 가져올 수 있음(받지 않으셔도 됨). 🐭 = 동물 연구(고전 원저라 넣었지만 사람 해부학 근거로는 보조용).", ""]
for label, want in [("1순위 — REVIEW.md가 ⚠️로 표시한 경로의 교체용", True), ("2순위 — 나머지 경로의 보강용", False)]:
    out += [f"### {label}", "", "| 받기 | 문헌 | DOI | 쓰이는 경로 | 기대하는 근거 |", "|---|---|---|---|---|"]
    for key, row in articles.items():
        uses = list(dict.fromkeys(row["uses"]))
        if bool(set(uses) & PRIORITY) != want:
            continue
        c = row["c"]
        fetch = "🆓" if row["free"] else "✅"
        if c.get("doi") in ANIMAL:
            fetch += " 🐭"
        ident = f"[{c['doi']}](https://doi.org/{c['doi']})" if c.get("doi") else (f"PMC {row['pmcid']}" if row.get("pmcid") else "DOI 없음")
        out.append(f"| {fetch} | {cell(c['citation'])} | {ident} | {', '.join(uses)} | {cell(c.get('why'))} |")
    out.append("")

n_fetch = sum(1 for r in articles.values() if not r["free"])
n_free = sum(1 for r in articles.values() if r["free"])
out.insert(6, f"규모: 책 {len(books)}권(핵심 4권), 논문 {len(articles)}편 — 그중 **받아 주실 논문 {n_fetch}편**, 무료 전문 {n_free}편.")
(HERE / "WANTED.md").write_text("\n".join(out), encoding="utf-8")
print("books", len(books), "articles", len(articles), "fetch", n_fetch, "free", n_free)
