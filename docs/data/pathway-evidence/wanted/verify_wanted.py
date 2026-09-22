#!/usr/bin/env python3
"""Re-check every candidate in the wanted/*.json files against Crossref and Europe PMC.

For each article: does the DOI resolve on Crossref, does its title match the agent's `crossrefTitle`
(fuzzy), is it a review / what year, and does Europe PMC say it is open access. For each book: does the
ISBN resolve on Google Books. Writes <file>.report.json next to the input and prints a summary.
"""
import difflib
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

GOOGLE_DOWN = True  # returns 429 for hours at a time; Open Library alone is enough
UA = {"User-Agent": "neuro-atlas-wanted-check/1 (mailto:byol9566@gmail.com)"}


def get(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(1.5 * (attempt + 1))
    return {"error": str(err)}


def norm(s):
    return " ".join("".join(c.lower() if c.isalnum() or c.isspace() else " " for c in (s or "")).split())


def check_article(c):
    out = {"doi": c.get("doi")}
    if not c.get("doi"):
        out["status"] = "NO_DOI"
        return out
    cr = get(f"https://api.crossref.org/works/{urllib.parse.quote(c['doi'], safe='/')}")
    msg = cr.get("message") if isinstance(cr, dict) else None
    if not msg:
        out["status"] = "DOI_NOT_ON_CROSSREF"
        out["crossref"] = cr.get("error", "no message")
        return out
    title = (msg.get("title") or [""])[0]
    year = (msg.get("issued", {}).get("date-parts") or [[None]])[0][0]
    out.update({"title": title, "journal": (msg.get("container-title") or [""])[0], "year": year, "type": msg.get("type")})
    ratio = difflib.SequenceMatcher(None, norm(title), norm(c.get("crossrefTitle") or c.get("citation"))).ratio()
    out["titleMatch"] = round(ratio, 2)
    epmc = get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:{urllib.parse.quote(c['doi'])}&format=json&resultType=lite")
    hits = (epmc.get("resultList") or {}).get("result") or []
    if hits:
        h = hits[0]
        out["epmc"] = {"pmid": h.get("pmid"), "pmcid": h.get("pmcid"), "isOpenAccess": h.get("isOpenAccess"), "pubType": h.get("pubType")}
        out["oaAgreed"] = (h.get("isOpenAccess") == c.get("oa"))
    else:
        out["epmc"] = None
    out["status"] = "OK" if ratio >= 0.6 else "TITLE_MISMATCH"
    return out


def check_book(c):
    out = {"isbn": c.get("isbn")}
    if not c.get("isbn"):
        out["status"] = "NO_ISBN"
        return out
    isbn = c["isbn"].split()[0].replace("-", "")  # "978... (print) / 978... (e-book)": take the first
    gb = get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}") if not GOOGLE_DOWN else {}
    items = gb.get("items") or []
    if items:
        info = items[0]["volumeInfo"]
        out.update({"title": info.get("title"), "publisher": info.get("publisher"), "year": info.get("publishedDate"), "status": "OK", "via": "google"})
        return out
    # Google Books rate-limits hard; Open Library is the fallback
    info = get(f"https://openlibrary.org/isbn/{isbn}.json")
    if not isinstance(info, dict) or not info.get("title"):
        out["status"] = "ISBN_NOT_FOUND"
        return out
    out.update({"title": info.get("title"), "publisher": ", ".join(info.get("publishers", [])), "year": info.get("publish_date"), "status": "OK", "via": "openlibrary"})
    return out


def main(paths):
    for p in map(Path, paths):
        data = json.loads(p.read_text(encoding="utf-8"))
        report = {"file": p.name, "batches": []}
        counts = {"OK": 0}
        for batch in data.get("batches", []):
            b = {"batch": batch.get("batch"), "pathways": []}
            for pw in batch.get("pathways", []):
                rows = []
                for c in pw.get("candidates", []):
                    r = check_book(c) if c.get("kind") == "book" else check_article(c)
                    r["citation"] = c.get("citation")
                    counts[r["status"]] = counts.get(r["status"], 0) + 1
                    rows.append(r)
                b["pathways"].append({"id": pw.get("id"), "candidates": rows})
            report["batches"].append(b)
        p.with_suffix(".report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print(p.name, counts)


if __name__ == "__main__":
    main(sys.argv[1:])
