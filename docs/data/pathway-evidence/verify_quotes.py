#!/usr/bin/env python3
"""Reviewer's tool: check that every quote in the collected evidence really occurs in the cited source.

    python3 verify_quotes.py [batch.json ...]        # default: every *.json next to this script

For each source it fetches the text the collector claims to have opened (Europe PMC full-text XML for
PMCIDs, the NCBI Bookshelf page for NBK ids), compares the recorded title/year/journal with Europe PMC's
metadata, and string-matches each quote after whitespace/punctuation normalisation. Results go to
`verification/<batch>.report.json`; fetched texts are cached in `verification/cache/`.

Statuses per quote: exact | fuzzy (>= 0.9 similarity to some window of the text) | NOT_FOUND | SOURCE_UNAVAILABLE.
Only `exact` and `fuzzy` count as verified. This says the words are in the paper -- whether the paper is a
good authority is a separate, human judgement recorded in REVIEW.md.
"""

import difflib
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "verification"
CACHE = OUT / "cache"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) neuro-atlas-evidence-check/1"}


def fetch(url: str, cache_name: str) -> str | None:
    path = CACHE / cache_name
    if path.exists():
        return path.read_text(errors="replace")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            text = r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"    fetch failed: {url} ({e})", file=sys.stderr)
        return None
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    time.sleep(0.4)  # be polite to the APIs
    return text


def normalise(text: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    text = text.replace("­", "").replace("‐", "-").replace("‑", "-").replace("–", "-").replace("—", "-")
    text = re.sub(r"[‘’]", "'", text)
    text = re.sub(r"[“”]", '"', text)
    text = re.sub(r"\[[\d,\s\-]+\]|\(\s*\d+(?:\s*[,\-]\s*\d+)*\s*\)", " ", text)  # numeric citation markers
    return re.sub(r"\s+", " ", text).strip().lower()


def match(quote: str, haystack: str) -> tuple[str, float]:
    q = normalise(quote)
    if not q:
        return "NOT_FOUND", 0.0
    if q in haystack:
        return "exact", 1.0
    # anchor on the rarest-looking words to find candidate windows, then compare fuzzily
    words = sorted(set(re.findall(r"[a-z]{6,}", q)), key=len, reverse=True)[:4]
    best = 0.0
    for w in words:
        for m in re.finditer(re.escape(w), haystack):
            start = max(0, m.start() - len(q))
            window = haystack[start : m.start() + len(q)]
            sm = difflib.SequenceMatcher(None, q, window, autojunk=False)
            blk = sm.find_longest_match(0, len(q), 0, len(window))
            lo = max(0, blk.b - blk.a)
            best = max(best, difflib.SequenceMatcher(None, q, window[lo : lo + len(q)], autojunk=False).ratio())
            if best >= 0.97:
                return "fuzzy", round(best, 3)
    return ("fuzzy" if best >= 0.9 else "NOT_FOUND"), round(best, 3)


def source_text(src: dict) -> tuple[str | None, dict]:
    """-> (normalised full text or None, metadata check)"""
    meta: dict = {}
    pmcid = (src.get("pmcid") or "").strip()
    nbk = (src.get("nbk") or "").strip()
    if pmcid:
        q = urllib.parse.quote(f"PMCID:{pmcid}")
        hit = fetch(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&format=json&resultType=core", f"{pmcid}.meta.json")
        if hit:
            results = json.loads(hit).get("resultList", {}).get("result", [])
            if results:
                r = results[0]
                meta = {
                    "registryTitle": r.get("title"),
                    "registryJournal": (r.get("journalInfo") or {}).get("journal", {}).get("title"),
                    "registryYear": r.get("pubYear"),
                    "registryLicense": r.get("license"),
                    "isOpenAccess": r.get("isOpenAccess"),
                    "pubTypes": (r.get("pubTypeList") or {}).get("pubType"),
                    "citedByCount": r.get("citedByCount"),
                    "titleSimilarity": round(difflib.SequenceMatcher(None, normalise(src.get("title", "")), normalise(r.get("title", ""))).ratio(), 2),
                    "yearMatches": str(src.get("year")) == str(r.get("pubYear")),
                }
            else:
                meta = {"error": "PMCID not found in Europe PMC"}
        xml = fetch(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML", f"{pmcid}.xml")
        if not xml:
            # author manuscripts and older free articles are on PMC but not in Europe PMC's XML set
            xml = fetch(f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/", f"{pmcid}.pmc.html")
            if xml and ("RecaptchaChallengePageUi" in xml or "cookies-required" in xml):
                # PMC rate-limits by serving a bot check with status 200: do not keep or match against it
                (CACHE / f"{pmcid}.pmc.html").unlink(missing_ok=True)
                meta["error"] = "PMC served a bot-check page instead of the article; retry later"
                xml = None
            if xml:
                meta["fullTextVia"] = "pmc-html"
        return (normalise(xml) if xml else None), meta
    if nbk:
        page = fetch(f"https://www.ncbi.nlm.nih.gov/books/{nbk}/?report=printable", f"{nbk}.html")
        if page:
            title = re.search(r"<title>(.*?)</title>", page, re.S)
            meta = {"registryTitle": html.unescape(title.group(1)).strip() if title else None}
        return (normalise(page) if page else None), meta
    url = (src.get("url") or "").strip()
    if url:
        page = fetch(url, re.sub(r"\W+", "_", url)[:120] + ".html")
        return (normalise(page) if page else None), {"note": "no PMCID/NBK: fetched the url as given"}
    return None, {"error": "source has no pmcid, nbk or url"}


def iter_quotes(node, path=""):
    """Yield (json path, source id, quote) for every object carrying both keys."""
    if isinstance(node, dict):
        if "quote" in node and "source" in node:
            yield path, node["source"], node["quote"]
        for k, v in node.items():
            if k != "sources":
                yield from iter_quotes(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from iter_quotes(v, f"{path}[{i}]")


def verify(batch_file: Path) -> dict:
    data = json.loads(batch_file.read_text())
    texts, source_report = {}, {}
    for src in data.get("sources", []):
        text, meta = source_text(src)
        texts[src["id"]] = text
        source_report[src["id"]] = {"claimed": {k: src.get(k) for k in ("title", "journal", "year", "pmcid", "nbk", "doi", "license", "type")}, "check": meta, "textAvailable": text is not None}
    quotes = []
    for path, sid, quote in iter_quotes(data):
        text = texts.get(sid)
        if sid not in texts:
            status, score = "UNKNOWN_SOURCE_ID", 0.0
        elif text is None:
            status, score = "SOURCE_UNAVAILABLE", 0.0
        else:
            status, score = match(quote, text)
        quotes.append({"path": path, "source": sid, "status": status, "score": score, "quote": quote})
    tally: dict[str, int] = {}
    for q in quotes:
        tally[q["status"]] = tally.get(q["status"], 0) + 1
    return {"batch": data.get("batch"), "file": batch_file.name, "tally": tally, "sources": source_report, "quotes": quotes}


def main(argv):
    files = [Path(a) for a in argv] or sorted(p for p in HERE.glob("*.json"))
    OUT.mkdir(exist_ok=True)
    for f in files:
        print(f"== {f.name}")
        report = verify(f)
        (OUT / f"{f.stem}.report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
        print("   quotes:", report["tally"])
        for sid, s in report["sources"].items():
            c = s["check"]
            flags = []
            if c.get("error"):
                flags.append(c["error"])
            if c.get("titleSimilarity") is not None and c["titleSimilarity"] < 0.8:
                flags.append(f"title mismatch ({c['titleSimilarity']}): registry says {c.get('registryTitle')!r}")
            if c.get("yearMatches") is False:
                flags.append(f"year mismatch: registry {c.get('registryYear')}")
            if not s["textAvailable"]:
                flags.append("full text unavailable")
            if flags:
                print(f"   {sid}: " + "; ".join(flags))
        for q in report["quotes"]:
            if q["status"] not in ("exact", "fuzzy"):
                print(f"   {q['status']:18s} {q['source']:4s} {q['path']}: {q['quote'][:90]!r}")


if __name__ == "__main__":
    main(sys.argv[1:])
