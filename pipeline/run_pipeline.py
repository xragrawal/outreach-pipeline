#!/usr/bin/env python3
"""Run the ICP to outreach pipeline, one stage at a time, with a gate per stage.

Usage
-----
    python3 pipeline/run_pipeline.py --dry-run
    python3 pipeline/run_pipeline.py --stage 1
    python3 pipeline/run_pipeline.py --stage all
    python3 pipeline/run_pipeline.py --stage 5 --confirm-credits

A gate is a cheap check that the stage output is usable. A failed gate stops
the run. Nothing is published if a gate fails.

Stage 5 calls a paid API. It does nothing unless you pass --confirm-credits.
"""

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
CONFIG = BASE / "pipeline.json"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    # the workdir in the file is relative to the repo root, not the caller's cwd
    base = Path(path).resolve().parent.parent
    cfg["project"]["workdir"] = str((base / cfg["project"]["workdir"]).resolve())
    return cfg


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def stage_by_id(cfg, sid):
    for s in cfg["stages"]:
        if str(s["id"]) == str(sid):
            return s
    raise SystemExit(f"no stage {sid}")


def resolve(cfg, rel):
    return (Path(cfg["project"]["workdir"]) / rel).resolve()


def ok(msg):
    print(f"  PASS  {msg}")


def bad(msg):
    print(f"  FAIL  {msg}")
    raise SystemExit(1)


def warn(msg):
    print(f"  WARN  {msg}")


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------

def gate_icp(cfg, stage):
    wd = Path(cfg["project"]["workdir"])
    icp = wd / "icp.md"
    if not icp.exists():
        warn("icp.md is missing. Stage 1 output should describe the ICP.")
    else:
        text = icp.read_text(encoding="utf-8").lower()
        missing = [s for s in stage.get("required_sections", []) if s.lower() not in text]
        if missing:
            bad(f"icp.md lacks sections: {missing}")
        ok(f"icp.md has {len(stage.get('required_sections', []))} required sections")

    tax = wd / "pipeline" / "taxonomy.csv"
    if not tax.exists():
        bad("pipeline/taxonomy.csv is missing")
    rows = read_csv(tax)
    if len(rows) < 5:
        bad(f"taxonomy has only {len(rows)} tags")
    total = 0.0
    for r in rows:
        try:
            w = float(r["weight"])
        except (KeyError, ValueError):
            bad(f"tag {r.get('tag')!r} has no numeric weight")
        if w <= 0:
            bad(f"tag {r['tag']!r} has weight {w}")
        if not r.get("regex", "").strip():
            bad(f"tag {r['tag']!r} has no regex")
        total += w
    core = [r for r in rows if r.get("core") == "yes"]
    if not core:
        bad("no core capability is marked")
    ok(f"taxonomy: {len(rows)} tags, {len(core)} core, weight sum {total:.2f}")
    if total < 1:
        warn("weight sum is below 1.0. Check the weight scale.")


def gate_source(cfg, stage):
    wd = Path(cfg["project"]["workdir"])
    src = (wd / stage["source_csv"]).resolve()
    out = wd / "universe.csv"

    if not src.exists():
        bad(f"source CSV not found: {src}")

    rows = read_csv(src)
    id_col = stage["id_column"]
    seen = set()
    dups = 0
    kept = []
    for r in rows:
        key = (r.get(id_col) or "").strip().lower()
        if not key:
            continue
        if key in seen:
            dups += 1
            continue
        seen.add(key)
        kept.append({k: (v or "").strip() for k, v in r.items()})

    if not kept:
        bad("source CSV has no usable rows")
    for f in stage["text_fields"]:
        if f not in kept[0]:
            bad(f"source CSV lacks text field {f!r}")

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(kept[0].keys()))
        w.writeheader()
        w.writerows(kept)

    ok(f"universe: {len(kept)} unique companies from {len(rows)} rows, {dups} duplicates dropped")
    ok(f"wrote {out.name}")
    if dups:
        warn("duplicates were dropped. Check that the first row was the right one.")


def gate_model(cfg, stage):
    terms = stage["terms"]
    total = sum(terms.values())
    if abs(total - 1.0) > 1e-9:
        bad(f"scoring terms sum to {total}, not 1.0")
    ok(f"terms sum to 1.0: " + ", ".join(f"{k} {v}" for k, v in terms.items()))

    tax = Path(cfg["project"]["workdir"]) / "pipeline" / "taxonomy.csv"
    rows = read_csv(tax)
    unweighted = [r["tag"] for r in rows if float(r["weight"]) <= 0]
    if unweighted:
        bad(f"tags with no weight: {unweighted}")
    ok(f"all {len(rows)} tags carry a weight")

    tiers = stage["tiers"]
    if [t["tier"] for t in tiers] != sorted(t["tier"] for t in tiers):
        bad("tiers are not in order")
    ok(f"{len(tiers)} tiers defined")


def gate_score(cfg, stage):
    wd = Path(cfg["project"]["workdir"])
    ranked = wd / "similarity-ranking.csv"
    kept_f = wd / "similarity-ranking-reachable.csv"
    gone_f = wd / "similarity-ranking-removed.csv"

    for p in (ranked, kept_f, gone_f):
        if not p.exists():
            bad(f"missing output: {p.name}")

    rows = read_csv(ranked)
    if not rows:
        bad("ranking is empty")
    scores = [float(r["score"]) for r in rows]
    if scores != sorted(scores, reverse=True):
        bad("ranking is not sorted by score")
    ok(f"ranking: {len(rows)} rows, sorted, top score {scores[0]}")

    kept = read_csv(kept_f)
    gone = read_csv(gone_f)
    if len(kept) + len(gone) != len(rows):
        bad(f"kept {len(kept)} + removed {len(gone)} != ranked {len(rows)}")
    ok(f"filter: {len(kept)} kept, {len(gone)} removed, total {len(rows)}")

    tiers = {}
    for r in rows:
        tiers[r.get("tier", "?")] = tiers.get(r.get("tier", "?"), 0) + 1
    ok(f"tiers: {tiers}")

    ties = {}
    for r in rows:
        ties[r["score"]] = ties.get(r["score"], 0) + 1
    worst = max(ties.items(), key=lambda x: x[1])
    if worst[1] > len(rows) * 0.1:
        warn(f"{worst[1]} companies tie at score {worst[0]}. Their order is not meaningful.")
    else:
        ok("no large tie block")

    limit = stage["reachability"]["headcount_limit"]
    over = [r["company"] for r in kept if (r.get("headcount") or "").isdigit()
            and int(r["headcount"]) >= limit]
    if over:
        bad(f"{len(over)} kept rows are at or above the headcount limit: {over[:5]}")
    ok(f"no kept row reaches the headcount limit of {limit}")


def gate_enrich(cfg, stage):
    wd = Path(cfg["project"]["workdir"])
    path = wd / "similarity-ranking-contacts.csv"
    if not path.exists():
        bad("similarity-ranking-contacts.csv is missing")
    rows = read_csv(path)

    allowed = set(stage["enrichment"]["status_values"])
    reject = set(stage["enrichment"]["reject_local_parts"])

    bad_status = {r["hunter_status"] for r in rows if r["hunter_status"] not in allowed}
    if bad_status:
        bad(f"unknown status values: {bad_status}")
    ok(f"status values are within {sorted(allowed)}")

    found = [r for r in rows if r["hunter_status"] == "found"]
    for r in found:
        if not r["contact_name"].strip():
            bad(f"{r['company']} is 'found' with no name")
        if not r["contact_email"].strip():
            bad(f"{r['company']} is 'found' with no email")
    ok(f"{len(found)} found rows all have a name and an email")

    leaked = []
    for r in rows:
        email = r["contact_email"].strip()
        if not email:
            continue
        local = email.split("@")[0].split("+")[0].split(".")[0].lower()
        if local in reject:
            leaked.append(email)
    if leaked:
        bad(f"generic addresses leaked through: {leaked[:5]}")
    ok("no generic address in the contact column")

    no_email = [r["company"] for r in rows if not r["contact_email"].strip()]
    ok(f"{len(rows) - len(no_email)} rows carry an email, {len(no_email)} are blank")

    from collections import Counter
    print("  INFO  status counts:", dict(Counter(r["hunter_status"] for r in rows)))


GATES = {
    "icp": gate_icp,
    "source": gate_source,
    "model": gate_model,
    "score": gate_score,
    "enrich": gate_enrich,
}


# ---------------------------------------------------------------------------
# runner
# ---------------------------------------------------------------------------

def run_command(cfg, stage, cmd, dry):
    label = " ".join(cmd)
    if dry:
        print(f"  PLAN  {label}")
        return
    print(f"  RUN   {label}")
    out = subprocess.run(cmd, cwd=cfg["project"]["workdir"])
    if out.returncode != 0:
        bad(f"command failed with code {out.returncode}: {label}")


def run_stage(cfg, stage, dry, confirm_credits):
    print(f"\n=== Stage {stage['id']}: {stage['name']} ===")
    print(f"  Q     {stage['question']}")

    if stage.get("requires_credits") and not confirm_credits and not dry:
        print("  SKIP  this stage spends API credits. Add --confirm-credits to run it.")
        return

    if stage.get("command"):
        run_command(cfg, stage, stage["command"], dry)
    if stage.get("post_command"):
        run_command(cfg, stage, stage["post_command"], dry)

    gate = GATES.get(stage.get("gate"))
    if not gate:
        return
    if dry:
        print(f"  PLAN  gate {stage['gate']}")
        return
    gate(cfg, stage)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(CONFIG))
    ap.add_argument("--stage", default="all")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm-credits", action="store_true")
    args = ap.parse_args()

    cfg = load_config(args.config)
    wd = cfg["project"]["workdir"]
    print(f"pipeline : {cfg['project']['name']}")
    print(f"subject  : {cfg['project']['subject']}")
    print(f"workdir  : {wd}")

    if args.stage == "all":
        stages = cfg["stages"]
    else:
        stages = [stage_by_id(cfg, s) for s in args.stage.split(",")]

    for s in stages:
        run_stage(cfg, s, args.dry_run, args.confirm_credits)

    print("\nDone.")


if __name__ == "__main__":
    main()
