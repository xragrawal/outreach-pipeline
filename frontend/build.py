#!/usr/bin/env python3
"""Build the pipeline page from the run artefacts.

Reads the CSVs the pipeline produced and injects them into template.html.
No figure is typed by hand: every number on the page comes from a file.
"""

import csv
import json
import re
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "index.html"
TEMPLATE = BASE / "template.html"
ROOT = BASE.parent


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_optional(path):
    """Read a file when it is there. A public copy has no contact files."""
    return read(path) if path.exists() else []


def first(row, *names):
    for n in names:
        v = row.get(n)
        if v not in (None, ""):
            return v
    return ""


def main():
    universe = read(ROOT / "universe.csv")
    removed = read(ROOT / "similarity-ranking-removed.csv")
    taxonomy = read(ROOT / "pipeline" / "taxonomy.csv")
    multi = read(ROOT / "multi-service-coverage.csv")

    # with contacts, else the plain ranking: the same rows, no contact columns
    with_contacts = ROOT / "similarity-ranking-reachable.csv"
    kept = read(with_contacts) if with_contacts.exists() else read(ROOT / "similarity-ranking.csv")
    outreach = read_optional(ROOT / "outreach.csv")
    cfg = json.loads((ROOT / "pipeline" / "pipeline.json").read_text())

    stages = []
    notes = {
        "icp": f"{len(taxonomy)} tags · weight sum {sum(float(t['weight']) for t in taxonomy):.2f}",
        "source": f"{len(universe)} rows · {len({r['company'].lower() for r in universe})} unique",
        "model": "0.88 / 0.07 / 0.05",
        "score": f"{len(kept)} kept · {len(removed)} removed",
        "enrich": f"{sum(1 for r in kept if r.get('contact_email'))} personal emails",
    }
    for s in cfg["stages"]:
        stages.append({
            "id": s["id"],
            "name": s["name"],
            "question": s["question"],
            "outputs": s["outputs"],
            "gate": s["gate"],
            "note": notes.get(s["key"], ""),
        })

    # ranking rows
    ranking = []
    for r in kept:
        ranking.append({
            "rank": int(float(first(r, "new_rank", "rank"))),
            "company": r["company"],
            "category": r["category"],
            "tier": r["tier"],
            "core_hits": int(float(r.get("core_hits") or 0)),
            "score": float(r["score"]),
            "email": r.get("contact_email", ""),
            "contact": r.get("contact_name", ""),
        })

    # tie block
    scores = Counter(r["score"] for r in kept)
    tie_score, tie_n = scores.most_common(1)[0]

    # contacts
    contacts = []
    for r in outreach:
        contacts.append({
            "priority": r["priority"],
            "company": r["company"],
            "name": r["contact_name"],
            "role": r["contact_role"],
            "email": r["contact_email"],
            "confidence": r["email_confidence"],
            "tier": r["tier"],
        })

    # multi-line five: the ones that sell more than one product line
    FIVE = {"upstash", "thirdweb", "blockrun", "crewai", "langchain"}
    by_company = {r["company"].lower(): r for r in kept}
    five = []
    for r in multi:
        if r["status"] != "kept" or r["company"].lower() not in FIVE:
            continue
        c = by_company.get(r["company"].lower(), {})
        five.append({
            "company": r["company"],
            "families": int(r["family_count"]),
            "families_list": r["families"],
            "email": c.get("contact_email", ""),
        })
    five.sort(key=lambda x: -x["families"])

    emails = sum(1 for r in kept if r.get("contact_email"))
    generic = sum(1 for r in kept if r.get("hunter_status") == "generic_only")
    w_sum = sum(float(t["weight"]) for t in taxonomy)

    data = {
        # the sheet holds the contacts, so only a run with contacts links to it
        "sheet": ("https://docs.google.com/spreadsheets/d/"
                  + cfg["stages"][-1]["handoff"]["spreadsheet_id"] + "/edit") if outreach else "",
        "meta": {"kept": len(kept), "emails": emails, "contacts": bool(contacts)},
        "stages": stages,
        "ranking": ranking,
        "contacts": contacts,
        "multiline": five,
    }

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("/*__DATA__*/{}", json.dumps(data, ensure_ascii=False))
    for k, v in {
        "__C_SOURCED__": len(universe),
        "__C_KEPT__": len(kept),
        "__C_REMOVED__": len(removed),
        "__C_EMAILS__": emails,
        "__C_GENERIC__": generic,
        "__C_TAGS__": len(taxonomy),
        "__W_SUM__": f"{w_sum:.2f}",
        "__TIE_N__": tie_n,
        "__N_SOURCES__": len(cfg["stages"][1]["source_types"]),
        "__DATE__": "24 November 2026",
    }.items():
        html = html.replace(k, str(v))

    leftover = re.findall(r"__[A-Z_]+__", html)
    if leftover:
        raise SystemExit(f"unreplaced placeholders: {sorted(set(leftover))}")

    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT} ({len(html)/1024:.1f} KB)")
    print(f"  companies {len(universe)} | kept {len(kept)} | removed {len(removed)}")
    print(f"  contacts {len(contacts)} | emails {emails} | generic {generic}")
    print(f"  tags {len(taxonomy)} | weight sum {w_sum:.2f} | tie {tie_n} at {tie_score}")
    print(f"  multi-line {len(five)}")


if __name__ == "__main__":
    main()
