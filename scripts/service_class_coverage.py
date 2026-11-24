#!/usr/bin/env python3
"""Score companies on how many infrastructure SERVICE CLASSES they sell.

These are not the subject's own capabilities. The classes are the generic ones
a buyer would name: cloud, database, payment, messaging, and so on. A company
that sells many classes has multi-service coverage.

Each class is detected from the company's category, service summary, and
service list. Rules are keyword based and auditable.
"""

import csv
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def resolve_run(arg):
    if arg:
        return Path(arg).resolve()
    cfg = json.loads((BASE / "pipeline" / "pipeline.json").read_text())
    return (BASE / cfg["run"]).resolve()

# class -> (label, regex)
CLASSES = {
    "cloud_compute": ("Cloud compute", r"serverless|virtual machine|\bvm\b|gpu|bare-?metal|dedicated server|cloud server|compute"),
    "hosting": ("Hosting and deployment", r"hosting|deploy|paas|application platform|static site|edge function"),
    "database": ("Database", r"database|postgres|mysql|mongo|redis|sql\b|key-value"),
    "storage": ("Storage", r"storage|object store|ipfs|file storage|block storage"),
    "networking": ("Networking, CDN, DNS", r"\bcdn\b|\bdns\b|proxy|load balanc|edge network|networking"),
    "messaging": ("Messaging, email, voice", r"email|sms|voice|telephony|messaging|speech|push notification"),
    "payments": ("Payments", r"payment|checkout|billing|onramp|on-ramp|fiat|settlement|merchant"),
    "wallets": ("Wallets and keys", r"wallet|key management|custody|smart account|account abstraction|multisig"),
    "identity": ("Identity and auth", r"identity|authentication|\bauth\b|\bkyc\b|authori[sz]ation|access control|permission"),
    "data_apis": ("Data APIs and analytics", r"data api|analytics|indexing|indexer|market data|explorer|enrichment|dataset"),
    "ai_model": ("AI and model inference", r"model inference|inference api|language model|hosted model|generation api|agent memory|vector"),
    "browser": ("Browser automation", r"browser session|browser automation|browser interaction|cloud browser"),
    "blockchain_rpc": ("Blockchain RPC and nodes", r"\brpc\b|node access|validator|staking"),
    "observability": ("Observability and evaluation", r"observability|tracing|evaluation|monitoring|logging"),
    "security": ("Security", r"security|audit|firewall|secret|vault|encryption"),
    "dev_tooling": ("Developer tooling", r"\bsdk\b|documentation|developer portal|feature flag|workflow|orchestrat|queue|runtime|sandbox"),
}

# Category names that map to a class without keyword help.
CATEGORY_HINT = {
    "Cloud compute": "cloud_compute",
    "Cloud compute and hosting": "cloud_compute",
    "Cloud compute and storage": "cloud_compute",
    "Cloud hosting": "hosting",
    "Cloud development infrastructure": "hosting",
    "Database infrastructure": "database",
    "Storage infrastructure": "storage",
    "Payment infrastructure": "payments",
    "Wallet infrastructure": "wallets",
    "Wallet and payment infrastructure": "wallets",
    "Identity infrastructure": "identity",
    "Authorization infrastructure": "identity",
    "Blockchain data APIs": "data_apis",
    "Blockchain data infrastructure": "data_apis",
    "Blockchain RPC and data APIs": "blockchain_rpc",
    "Model inference": "ai_model",
    "Browser infrastructure": "browser",
    "Email infrastructure": "messaging",
    "Voice infrastructure": "messaging",
    "AI evaluation and observability": "observability",
    "Agent observability": "observability",
    "Agent orchestration and observability": "observability",
    "Agent memory": "ai_model",
    "Analysis and data": "data_apis",
}


def classes_for(row, cols=None):
    cols = cols or {}
    cat = cols.get("category", "category")
    summary = cols.get("summary", "service_summary")
    services = cols.get("services", "services")
    text = " | ".join([str(row.get(cat, "")), str(row.get(summary, "")),
                       str(row.get(services, ""))]).lower()
    found = set()
    hint = CATEGORY_HINT.get(row.get(cat, ""))
    if hint:
        found.add(hint)
    for key, (_, pat) in CLASSES.items():
        if re.search(pat, text):
            found.add(key)
    return found


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=None, help="run folder (default: pipeline.json)")
    args = ap.parse_args()

    run_dir = resolve_run(args.run)
    run = json.loads((run_dir / "run.json").read_text()) if (run_dir / "run.json").exists() else {}
    cols = run.get("columns", {})
    src = run_dir / run.get("source_csv", "universe.csv")
    out_path = run_dir / "service-class-coverage.csv"

    id_col = cols.get("id", "company")
    url_col = cols.get("url", "url")
    cat_col = cols.get("category", "category")
    seg_col = cols.get("segment", "segment")
    hc_col = cols.get("headcount", "headcount")
    svc_col = cols.get("services", "services")

    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
    out = []
    for r in rows:
        cls = classes_for(r, cols)
        out.append({
            "company": r.get(id_col, ""),
            "url": r.get(url_col, ""),
            "category": r.get(cat_col, ""),
            "segment": r.get(seg_col, ""),
            "headcount": r.get(hc_col, ""),
            "class_count": len(cls),
            "service_classes": "; ".join(sorted(CLASSES[k][0] for k in cls)),
            "services": r.get(svc_col, ""),
        })

    out.sort(key=lambda x: (-x["class_count"], x["company"].lower()))
    for i, r in enumerate(out, 1):
        r["rank"] = i

    fields = ["rank", "company", "class_count", "service_classes", "category",
              "segment", "headcount", "url", "services"]
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)

    dist = Counter(r["class_count"] for r in out)
    print(f"wrote {out_path}")
    print("\ncoverage distribution:")
    for n in sorted(dist, reverse=True):
        print(f"  {n:2d} classes: {dist[n]:3d} companies")
    print(f"\ntop 25 of {len(out)}:")
    print(f"{'#':>3} {'company':20s} {'n':>2}  classes")
    for r in out[:25]:
        print(f"{r['rank']:3d} {r['company'][:20]:20s} {r['class_count']:2d}  {r['service_classes'][:110]}")

    # per-class totals
    per = Counter()
    for r in out:
        for c in r["service_classes"].split("; "):
            if c:
                per[c] += 1
    print("\ncompanies per class:")
    for c, n in per.most_common():
        print(f"  {n:3d}  {c}")


if __name__ == "__main__":
    main()
