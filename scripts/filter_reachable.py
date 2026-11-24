#!/usr/bin/env python3
"""Filter a similarity ranking down to companies that are feasible to approach.

Two rules decide removal:

  Rule 1  Headcount is at or above the run's limit.
  Rule 2  The company is on the run's removal list: a hyperscaler, a public
          company, a category leader, a competitor, or a supplier.

Both rules live in `run.json`, so the filter carries no company names of its own.
Every removal keeps a reason code, so the decision can be reversed.

Usage
-----
    python3 scripts/filter_reachable.py --run examples/usebuy
"""

import argparse
import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DEFAULT_HEADCOUNT_LIMIT = 150


def resolve_run(arg):
    if arg:
        return Path(arg).resolve()
    cfg = json.loads((BASE / "pipeline" / "pipeline.json").read_text())
    return (BASE / cfg["run"]).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=None, help="run folder (default: pipeline.json)")
    args = ap.parse_args()

    run_dir = resolve_run(args.run)
    run = json.loads((run_dir / "run.json").read_text())
    reach = run.get("reachability", {})
    cols = run.get("columns", {})

    headcount_limit = reach.get("headcount_limit", DEFAULT_HEADCOUNT_LIMIT)
    remove = {k: tuple(v) for k, v in reach.get("remove", {}).items()}
    suppliers = reach.get("suppliers", {})

    src_path = run_dir / run.get("source_csv", "universe.csv")
    rank_path = run_dir / "similarity-ranking.csv"
    out_path = run_dir / "similarity-ranking-reachable.csv"
    removed_path = run_dir / "similarity-ranking-removed.csv"

    hc_col = cols.get("headcount", "headcount")
    id_col = cols.get("id", "company")

    rank = list(csv.DictReader(open(rank_path)))
    src = {r.get(id_col, ""): r for r in csv.DictReader(open(src_path, encoding="utf-8-sig"))}

    kept, removed = [], []
    for r in rank:
        name = r["company"]
        hc_raw = str(src.get(name, {}).get(hc_col, "")).strip()
        hc = int(hc_raw) if hc_raw.isdigit() else None

        reason = None
        if name in remove:
            reason = remove[name]
        elif hc is not None and hc >= headcount_limit:
            reason = (f"headcount {hc}", "above the size limit")

        if reason:
            removed.append({**r, "headcount": hc_raw or "",
                            "reason_code": reason[0], "reason": reason[1]})
        else:
            kept.append({**r, "headcount": hc_raw or "",
                         "size_band": ("small" if hc is not None and hc < 50 else
                                       "mid" if hc is not None else "unknown"),
                         "supplier": suppliers.get(name, "")})

    for i, r in enumerate(kept, 1):
        r["new_rank"] = i
        r["old_rank"] = r["rank"]

    fields = ["new_rank", "old_rank", "company", "url", "segment", "category", "score",
              "match_index", "capability_match", "core_hits", "tier", "headcount",
              "size_band", "supplier", "matched_capabilities", "services", "pricing_route"]
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(kept)

    with open(removed_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["old_rank", "company", "score", "category",
                                          "headcount", "reason_code", "reason"],
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(removed, key=lambda r: -float(r["score"])))

    print(f"run      : {run_dir}")
    print(f"kept {len(kept)}  removed {len(removed)}  total {len(kept) + len(removed)}")
    print(f"\nwrote {out_path}")
    print(f"wrote {removed_path}")
    print(f"\n{'#':>3} {'company':22s} {'score':>5} {'old':>4} {'hc':>4}  matched")
    for r in kept[:20]:
        print(f"{r['new_rank']:3d} {r['company'][:22]:22s} {r['score']:>5} {r['old_rank']:>4} "
              f"{r['headcount'] or '-':>4}  {r['matched_capabilities'][:60]}")


if __name__ == "__main__":
    main()
