#!/usr/bin/env python3
"""Start a new run: one folder, empty artefacts, a config with the defaults.

The engine reads everything about the subject from a run folder. This script
makes that folder, so a new ICP starts from a known shape and not from a copy of
someone else's run.

Usage
-----
    python3 scripts/new_run.py --slug acme --subject "Acme.ai"
    python3 scripts/new_run.py --slug acme --subject "Acme.ai" --dir examples
    python3 scripts/new_run.py --slug acme --subject "Acme.ai" --force
"""

import argparse
import datetime
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TEMPLATE = BASE / "pipeline" / "run.template.json"

ICP = """# ICP: {subject}

## Buyer

TODO: who pays, what they need, how they pay, what they refuse.

## Value proposition

TODO: the three or four things {subject} actually sells.

## Capability surface

TODO: one line per capability. Name it as a buyer would.

## Weights

TODO: the weight of each capability, and the evidence behind it.

## Core capabilities

TODO: the tags that must match. Two core hits is the tier 1 floor.

## Anti-ICP

TODO: who is out of scope, and why.

## Evidence

TODO: where the numbers come from. Date every source.
"""

SCORING = """# Scoring model: {subject}

| Field | Value |
|---|---|
| Terms | capability 0.88, delivery 0.07, buyer 0.05 |
| Tier 1 | match index 55 or more, 2 or more core hits |
| Tier 2 | match index 18 or more, 1 or more core hit |
| Tier 3 | everything else |

## Why capability carries 0.88

TODO: defend the weights with evidence from the product.

## Tiers

TODO: say what a tier 1 company looks like, in one line.
"""

RUN_README = """# Run: {subject}

| Field | Value |
|---|---|
| Subject | {subject} |
| Started | {date} |
| Folder | `{slug}` |

## Steps

1. Fill `icp.md` and `taxonomy.csv`.
2. Run stage 2 to source `universe.csv` automatically.
3. Write `scoring-model.md`.
4. Run stage 4 to score, stage 5 to enrich.
5. Build the page.

```bash
python3 pipeline/run_pipeline.py --run {rel} --stage 1,2,3
python3 pipeline/run_pipeline.py --run {rel} --stage 4
python3 pipeline/run_pipeline.py --run {rel} --stage 5 --confirm-credits
python3 frontend/build.py --run {rel}
```

## Files

| File | Holds |
|---|---|
| `run.json` | Subject, column map, model terms, tier cuts, reachability, enrichment, handoff |
| `icp.md` | The target profile |
| `taxonomy.csv` | Capability tags with weight, core flag and regex |
| `universe.csv` | The sourced companies |
| `scoring-model.md` | How the weights were set |
"""

UNIVERSE_HEADER = ["company", "url", "segment", "category", "service_summary",
                   "services", "sales_route", "evidence_type", "headcount"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True, help="folder name, for example acme")
    ap.add_argument("--subject", required=True, help='the target, for example "Acme.ai"')
    ap.add_argument("--dir", default="runs", help="parent folder (default: runs)")
    ap.add_argument("--force", action="store_true", help="write into an existing folder")
    args = ap.parse_args()

    slug = args.slug.strip().lower().replace(" ", "-")
    run_dir = (BASE / args.dir / slug).resolve()
    if run_dir.exists() and not args.force:
        raise SystemExit(f"{run_dir} exists. Add --force to write into it.")
    run_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.date.today().isoformat()
    run = json.loads(TEMPLATE.read_text())
    run.update({"name": slug, "subject": args.subject, "date": today})
    (run_dir / "run.json").write_text(json.dumps(run, indent=2) + "\n")

    (run_dir / "icp.md").write_text(ICP.format(subject=args.subject))
    (run_dir / "scoring-model.md").write_text(SCORING.format(subject=args.subject))
    (run_dir / "taxonomy.csv").write_text("tag,weight,core,regex\n")
    (run_dir / "universe.csv").write_text(",".join(UNIVERSE_HEADER) + "\n")
    (run_dir / "README.md").write_text(
        RUN_README.format(subject=args.subject, date=today, slug=slug,
                          rel=run_dir.relative_to(BASE)))

    rel = run_dir.relative_to(BASE)
    print(f"made  {run_dir}")
    print(f"run   {rel}")
    print("\nnext:")
    print(f"  1. write {rel}/icp.md and {rel}/taxonomy.csv")
    print(f"  2. run automatic sourcing for {rel}/universe.csv")
    print(f"  3. python3 pipeline/run_pipeline.py --run {rel} --stage 1,2,3")
    print(f"  4. python3 pipeline/run_pipeline.py --run {rel} --stage 4")
    print(f"  5. python3 frontend/build.py --run {rel}")
    print(f"\nor serve it: python3 frontend/serve.py --run {rel}")


if __name__ == "__main__":
    main()
