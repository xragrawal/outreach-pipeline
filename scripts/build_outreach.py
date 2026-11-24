#!/usr/bin/env python3
"""Turn the contact table into the outreach handoff.

Reads `similarity-ranking-contacts.csv`, keeps the rows with a personal
address, and writes `outreach.csv`: one row per person to write to, in the
order to write to them.

The priority map and the reason template live in `run.json` under `handoff`,
so nothing about the subject is in this file.

Usage
-----
    python3 scripts/build_outreach.py --run examples/usebuy
"""

import argparse
import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DEFAULT_PRIORITY = {"1": "now", "2": "this week", "3": "batch"}
DEFAULT_REASON = "Sells {caps}."
MAX_CAPS = 3

FIELDS = ["priority", "company", "contact_name", "contact_role", "contact_email",
          "email_confidence", "tier", "score", "match_index", "core_hits",
          "reason_to_contact", "url"]


def resolve_run(arg):
    if arg:
        return Path(arg).resolve()
    cfg = json.loads((BASE / "pipeline" / "pipeline.json").read_text())
    return (BASE / cfg["run"]).resolve()


def human(caps, limit=MAX_CAPS):
    """`api_gateway; web_search` becomes `api gateway, web search`."""
    parts = [c.strip().replace("_", " ") for c in caps.split(";") if c.strip()]
    return ", ".join(parts[:limit])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=None, help="run folder (default: pipeline.json)")
    args = ap.parse_args()

    run_dir = resolve_run(args.run)
    run = json.loads((run_dir / "run.json").read_text()) if (run_dir / "run.json").exists() else {}
    handoff = run.get("handoff", {})
    priority = {str(k): v for k, v in (handoff.get("priority") or DEFAULT_PRIORITY).items()}
    reason = handoff.get("reason") or DEFAULT_REASON

    src = run_dir / "similarity-ranking-contacts.csv"
    out_path = run_dir / "outreach.csv"
    if not src.exists():
        raise SystemExit(f"no contact table: {src}\nRun the enrichment stage first.")

    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
    picked = [r for r in rows
              if (r.get("hunter_status") == "found" and (r.get("contact_email") or "").strip())]

    order = {label: i for i, label in enumerate(dict.fromkeys(priority.values()))}
    out = []
    for r in picked:
        tier = (r.get("tier") or "").strip()
        label = priority.get(tier[:1], "batch")
        out.append({
            "priority": label,
            "company": r.get("company", ""),
            "contact_name": r.get("contact_name", ""),
            "contact_role": r.get("contact_role", ""),
            "contact_email": r.get("contact_email", ""),
            "email_confidence": r.get("email_confidence", ""),
            "tier": tier,
            "score": r.get("score", ""),
            "match_index": r.get("match_index", ""),
            "core_hits": r.get("core_hits", ""),
            "reason_to_contact": reason.format(caps=human(r.get("matched_capabilities", ""))),
            "url": r.get("url", ""),
        })

    out.sort(key=lambda r: (order.get(r["priority"], 99), -float(r["score"] or 0)))

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)

    counts = {}
    for r in out:
        counts[r["priority"]] = counts.get(r["priority"], 0) + 1
    print(f"run   : {run_dir}")
    print(f"rows  : {len(rows)} contacts, {len(out)} with a personal address")
    print(f"order : " + ", ".join(f"{k} {v}" for k, v in counts.items()) if counts else "order : none")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
