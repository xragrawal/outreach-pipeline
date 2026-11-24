#!/usr/bin/env python3
"""Rank a company CSV by similarity to a subject, weighted on capabilities.

Model
-----
1. The subject vector comes from the run's taxonomy: one weight per tag.
2. Every company gets a capability vector from its category, summary and
   service list, using the regex rules in the same taxonomy.
3. Capability match = weighted Jaccard over the two vectors. It answers: how
   much of the subject's weighted capability surface does this company cover?
4. Two small tie-breakers are added: delivery model and buyer.

    score = capability * match_index + delivery * delivery + buyer * buyer

Capability dominates. The terms come from run.json, not from this file.

Usage
-----
    python3 scripts/rank_similarity.py --run examples/usebuy

The run folder holds `run.json`, `taxonomy.csv` and the source CSV.
"""

import argparse
import csv
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

DEFAULT_COLUMNS = {
    "id": "company",
    "url": "url",
    "segment": "segment",
    "category": "category",
    "summary": "service_summary",
    "services": "services",
    "sales_route": "sales_route",
    "evidence_type": "evidence_type",
}

DEFAULT_TERMS = {"capability": 0.88, "delivery": 0.07, "buyer": 0.05}
DEFAULT_TIERS = [
    {"tier": 1, "match_index_min": 55, "core_hits_min": 2},
    {"tier": 2, "match_index_min": 18, "core_hits_min": 1},
]
DEFAULT_TIER_LABELS = {1: "1 direct", 2: "2 adjacent", 3: "3 different layer"}
DEFAULT_DELIVERY = {
    "published_pricing_prefix": "Published pricing",
    "points_published": 0.45,
    "points_metered": 0.30,
    "points_protocol": 0.15,
    "points_evidence": 0.10,
    "evidence_value": "company_service_page",
    "protocol_pattern": r"\bmcp\b",
}


def resolve_run(arg):
    """The run folder: --run, else the one named in pipeline/pipeline.json."""
    if arg:
        return Path(arg).resolve()
    cfg = json.loads((BASE / "pipeline" / "pipeline.json").read_text())
    return (BASE / cfg["run"]).resolve()


def load_run(run_dir):
    run = json.loads((run_dir / "run.json").read_text())
    tax = list(csv.DictReader(open(run_dir / "taxonomy.csv", encoding="utf-8-sig")))
    weights = {r["tag"]: float(r["weight"]) for r in tax}
    # a tag may carry a guard: a second regex that must also match the text
    rules = [(r["tag"], r["regex"], (r.get("guard") or "").strip())
             for r in tax if r.get("regex", "").strip()]
    core = {r["tag"] for r in tax if str(r.get("core", "")).strip().lower() in ("1", "true", "yes")}
    return run, weights, rules, core


def tag_company(row, rules, cols):
    text = " | ".join([
        str(row.get(cols["category"], "")),
        str(row.get(cols["summary"], "")),
        str(row.get(cols["services"], "")),
    ]).lower()
    tags = set()
    for tag, pat, guard in rules:
        if re.search(pat, text) and (not guard or re.search(guard, text)):
            tags.add(tag)
    return tags


def wjaccard(a, b, weights):
    inter = sum(weights[t] for t in (a & b))
    union = sum(weights[t] for t in (a | b))
    return inter / union if union else 0.0


def delivery_score(row, cols, metered, dcfg):
    s = 0.0
    if str(row.get(cols["sales_route"], "")).startswith(dcfg["published_pricing_prefix"]):
        s += dcfg["points_published"]
    if row.get(cols["category"]) in metered:
        s += dcfg["points_metered"]
    if re.search(dcfg["protocol_pattern"], str(row.get(cols["services"], "")), re.I):
        s += dcfg["points_protocol"]
    if row.get(cols["evidence_type"]) == dcfg["evidence_value"]:
        s += dcfg["points_evidence"]
    return min(s, 1.0)


def tier_for(match_index, core_hits, tiers):
    for t in sorted(tiers, key=lambda x: x["tier"]):
        if match_index >= t["match_index_min"] and core_hits >= t["core_hits_min"]:
            return t["tier"]
    return 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=None, help="run folder (default: pipeline.json)")
    args = ap.parse_args()

    run_dir = resolve_run(args.run)
    run, weights, rules, core = load_run(run_dir)

    cols = {**DEFAULT_COLUMNS, **run.get("columns", {})}
    model = run.get("model", {})
    terms = {**DEFAULT_TERMS, **model.get("terms", {})}
    tiers = model.get("tiers") or DEFAULT_TIERS
    labels = {int(k): v for k, v in model.get("tier_labels", {}).items()} or DEFAULT_TIER_LABELS
    buyer_weights = model.get("buyer_weights", {})
    buyer_default = model.get("buyer_default", 0.25)
    metered = set(model.get("metered_categories", []))
    dcfg = {**DEFAULT_DELIVERY, **model.get("delivery", {})}

    src = run_dir / run.get("source_csv", "universe.csv")
    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))

    subject = set(weights)
    results = []
    for r in rows:
        tags = tag_company(r, rules, cols)
        cap = wjaccard(subject, tags, weights)
        matched = sorted((t for t in (subject & tags)), key=lambda t: (-weights[t], t))
        results.append({
            "company": r.get(cols["id"], ""),
            "url": r.get(cols["url"], ""),
            "segment": r.get(cols["segment"], ""),
            "category": r.get(cols["category"], ""),
            "capability_match": round(cap * 100, 1),
            "delivery": round(delivery_score(r, cols, metered, dcfg) * 100, 1),
            "buyer": round(buyer_weights.get(r.get(cols["category"]), buyer_default) * 100, 1),
            "matched_capabilities": "; ".join(matched),
            "services": r.get(cols["services"], ""),
            "pricing_route": r.get(cols["sales_route"], ""),
        })

    best = max((r["capability_match"] for r in results), default=0)
    for r in results:
        r["match_index"] = round(r["capability_match"] / best * 100, 1) if best else 0
        r["score"] = round(
            terms["capability"] * r["match_index"]
            + terms["delivery"] * r["delivery"]
            + terms["buyer"] * r["buyer"], 1)
        hits = sum(1 for t in r["matched_capabilities"].split("; ") if t in core)
        r["core_hits"] = hits
        tier = tier_for(r["match_index"], hits, tiers)
        r["tier"] = labels.get(tier, str(tier))

    results.sort(key=lambda r: (-r["score"], -r["capability_match"], -r["core_hits"], r["company"].lower()))

    out = run_dir / "similarity-ranking.csv"
    fields = ["rank", "tier", "company", "url", "segment", "category", "score", "match_index",
              "capability_match", "core_hits", "delivery", "buyer", "matched_capabilities",
              "services", "pricing_route"]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for i, r in enumerate(results, 1):
            r["rank"] = i
            w.writerow(r)

    print(f"run      : {run_dir}")
    print(f"subject  : {run.get('subject', '')}")
    print(f"wrote {out}  ({len(results)} rows)")
    print(f"{'#':>3} {'company':22s} {'score':>6} {'cap':>6} {'idx':>5}  matched")
    for r in results[:40]:
        print(f"{r['rank']:3d} {r['company'][:22]:22s} {r['score']:6.1f} "
              f"{r['capability_match']:6.1f} {r['match_index']:5.0f}  {r['matched_capabilities'][:70]}")


if __name__ == "__main__":
    main()
