#!/usr/bin/env python3
"""Build the pipeline page from a run folder.

Reads the CSVs the run produced and injects them into template.html. No figure
is typed by hand: every number on the page comes from a file.

Usage
-----
    python3 frontend/build.py
    python3 frontend/build.py --run examples/usebuy
"""

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
OUT = BASE / "index.html"
TEMPLATE = BASE / "template.html"


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


def resolve_run(arg):
    if arg:
        return Path(arg).resolve()
    cfg = json.loads((ROOT / "pipeline" / "pipeline.json").read_text())
    return (ROOT / cfg["run"]).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=None, help="run folder (default: pipeline.json)")
    args = ap.parse_args()

    run_dir = resolve_run(args.run)
    run = json.loads((run_dir / "run.json").read_text()) if (run_dir / "run.json").exists() else {}
    cfg = json.loads((ROOT / "pipeline" / "pipeline.json").read_text())

    universe = read(run_dir / "universe.csv")
    removed = read(run_dir / "similarity-ranking-removed.csv")
    taxonomy = read(run_dir / "taxonomy.csv")
    multi = read(run_dir / "multi-service-coverage.csv")

    # with contacts, else the plain ranking: the same rows, no contact columns
    with_contacts = run_dir / "similarity-ranking-reachable.csv"
    kept = read(with_contacts) if with_contacts.exists() else read(run_dir / "similarity-ranking.csv")
    outreach = read_optional(run_dir / "outreach.csv")

    w_sum = sum(float(t["weight"]) for t in taxonomy)
    emails = sum(1 for r in kept if r.get("contact_email"))
    generic = sum(1 for r in kept if r.get("hunter_status") == "generic_only")

    stages = []
    notes = {
        "icp": f"{len(taxonomy)} tags · weight sum {w_sum:.2f}",
        "source": f"{len(universe)} rows · {len({r['company'].lower() for r in universe})} unique",
        "model": " / ".join(f"{v:g}" for v in run.get("model", {}).get("terms", {}).values()) or "",
        "score": f"{len(kept)} kept · {len(removed)} removed",
        "enrich": (f"{emails} personal emails" if outreach
                   else "contacts withheld from this copy"),
    }
    for s in cfg["stages"]:
        stages.append({
            "id": s["id"],
            "name": s["name"],
            "question": s["question"],
            "outputs": s["outputs"],
            "gate": s["gate"],
            "credits": bool(s.get("requires_credits")),
            "note": notes.get(s["key"], ""),
        })

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

    # the tie report matches the stage 4 gate, which reads the full ranking
    full = read(run_dir / "similarity-ranking.csv")
    scores = Counter(r["score"] for r in full)
    tie_score, tie_n = scores.most_common(1)[0]

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

    # the companies that sell the most product lines, reachable ones only
    by_company = {r["company"].lower(): r for r in kept}
    multiline = []
    for r in multi:
        if r["status"] != "kept" or r["company"].lower() not in by_company:
            continue
        c = by_company[r["company"].lower()]
        multiline.append({
            "company": r["company"],
            "families": int(r["family_count"]),
            "families_list": r["families"],
            "email": c.get("contact_email", ""),
        })
    multiline.sort(key=lambda x: (-x["families"], x["company"].lower()))
    multiline = multiline[:5]

    sheet_id = run.get("handoff", {}).get("spreadsheet_id", "")
    data = {
        # the sheet holds the contacts, so only a run with contacts links to it
        "sheet": (f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
                  if sheet_id and outreach else ""),
        "meta": {"kept": len(kept), "emails": emails, "contacts": bool(contacts),
                 "multiline": len(multiline)},
        "stages": stages,
        "ranking": ranking,
        "contacts": contacts,
        "multiline": multiline,
    }

    # a run without contacts must not claim zero. Say the data is not here.
    if contacts:
        email_metric = (f'<div class="figure" data-count="{emails}">0</div>\n'
                        f'        <div class="note">{generic} shared inboxes refused</div>')
    else:
        email_metric = ('<div class="figure word">withheld</div>\n'
                        '        <div class="note">personal addresses stay out of this copy</div>')

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("/*__DATA__*/{}", json.dumps(data, ensure_ascii=False))
    for k, v in {
        "__C_SOURCED__": len(universe),
        "__C_KEPT__": len(kept),
        "__C_REMOVED__": len(removed),
        "__EMAIL_METRIC__": email_metric,
        "__C_GENERIC__": generic,
        "__C_TAGS__": len(taxonomy),
        "__W_SUM__": f"{w_sum:.2f}",
        "__TIE_N__": tie_n,
        "__N_SOURCES__": len(cfg["stages"][1].get("source_types", [])),
        "__SUBJECT__": run.get("subject", ""),
        "__DATE__": run.get("date", ""),
    }.items():
        html = html.replace(k, str(v))

    leftover = re.findall(r"__[A-Z_]+__", html)
    if leftover:
        raise SystemExit(f"unreplaced placeholders: {sorted(set(leftover))}")

    OUT.write_text(html, encoding="utf-8")
    print(f"run   : {run_dir}")
    print(f"wrote {OUT} ({len(html)/1024:.1f} KB)")
    print(f"  companies {len(universe)} | kept {len(kept)} | removed {len(removed)}")
    print(f"  contacts {len(contacts)} | emails {emails} | generic {generic}")
    print(f"  tags {len(taxonomy)} | weight sum {w_sum:.2f} | tie {tie_n} at {tie_score}")
    print(f"  multi-line {len(multiline)}")


if __name__ == "__main__":
    main()
