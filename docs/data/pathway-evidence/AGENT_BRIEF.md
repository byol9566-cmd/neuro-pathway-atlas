# Evidence collection brief (for collection sub-agents)

Project: a web 3D neuroanatomy learning tool for medical students. Clicking a neural pathway highlights the
participating structures step by step. We need a **citable, machine-readable evidence base** for each pathway.
A separate reviewer will verify every citation, so **traceability matters more than volume**.

## Hard rules
- You COLLECT; you do not judge the project. Write exactly ONE file: the JSON path given in your task. Touch nothing else.
- Do NOT spawn sub-agents. Use at most **3 WebSearch calls** in total (the session quota is nearly exhausted).
  Search the literature through APIs with WebFetch or `curl` instead:
  - Europe PMC search: `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=<q>&format=json&pageSize=10&resultType=lite`
    Useful filters inside `<q>`: `OPEN_ACCESS:y`, `PUB_TYPE:review`, `TITLE:"..."`, `HAS_FT:y`. URL-encode the query.
  - Europe PMC full text (open-access only): `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC1234567/fullTextXML`
  - NCBI Bookshelf chapters (StatPearls; Purves *Neuroscience* 2nd ed.): `https://www.ncbi.nlm.nih.gov/books/NBK<id>/`
    Find StatPearls chapters via `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=books&term=<q>&retmode=json`
- **Only cite a source whose text you actually opened in this session.** Never cite from memory, never invent
  PMCIDs/DOIs/page numbers. If you know a fact but could not find an openable source for it, put it under
  `unsourced` — do not attach a citation to it.
- Every claim needs a **verbatim quote (8–45 words)** copied from the opened text, exactly as written (the reviewer
  will string-match it against the full text). No paraphrase inside `quote`. No ellipses inside a quote.
- Prefer, in order: peer-reviewed review articles / anatomy papers with a PMCID (open access) > Purves *Neuroscience*
  (NCBI Bookshelf) > StatPearls. Avoid predatory/unknown journals, blogs, Wikipedia, Kenhub, TeachMeAnatomy, course notes.
- Where sources disagree (e.g. level of a decussation, which nucleus), record BOTH under `conflicts` — do not pick one.
- Human anatomy. If a statement comes from animal work, set `"species"` accordingly.
- Aim for 2 independent sources for each pathway's core chain when available. Stop after ~45 tool calls; partial but
  clean output beats complete but sloppy.

## Output schema (one JSON object per file)
```json
{
  "batch": "<batch id>",
  "collectedBy": "sub-agent",
  "sources": [
    { "id": "S1", "type": "review | primary | textbook | statpearls",
      "title": "", "authors": "First AB, et al.", "journal": "", "year": 2020,
      "pmcid": "PMC...", "pmid": "", "doi": "", "nbk": "NBK...", "url": "",
      "license": "exact license text as shown in the source, or 'not stated'",
      "openedVia": "europepmc-fulltext | bookshelf | publisher-html" }
  ],
  "pathways": [
    { "id": "kebab-case-id", "name": "", "category": "", "function": "",
      "steps": [
        { "order": 1, "neuronOrder": 1,
          "cellBodies": "structure containing the somata",
          "courseVia": ["tracts / fascicles / nerve, in order"],
          "terminatesIn": "structure where the axon synapses",
          "laterality": "ipsilateral | contralateral | bilateral | midline (relative to the side of origin)",
          "decussation": { "present": false, "where": "" },
          "neurotransmitter": "",
          "evidence": [ { "source": "S1", "quote": "", "species": "human" } ] }
      ],
      "lesions": [ { "site": "", "deficit": "", "side": "ipsilateral | contralateral | bilateral", "evidence": [ { "source": "S1", "quote": "" } ] } ],
      "conflicts": [ { "issue": "", "positions": [ { "claim": "", "source": "S1", "quote": "" } ] } ],
      "unsourced": [ "facts you believe true but could not source from an opened text" ]
    }
  ]
}
```
Validate that the file parses as JSON before you finish (`python3 -m json.tool <file> > /dev/null`).

## Final message
Reply with a short report only: pathways covered, number of sources, anything you could not source, any conflicts found.
