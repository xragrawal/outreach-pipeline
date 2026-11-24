#!/usr/bin/env python3
"""Filter the similarity ranking down to companies that are feasible to approach.

Two rules decide removal:

  Rule 1  Headcount from the CSV is 150 or more.
  Rule 2  The company is a hyperscaler, a public company, a category leader with a
          large sales organisation, or a division of one. The CSV has no headcount
          for the AI segment, so these calls are made on brand and market position.

Every removal carries a reason code so the decision can be reversed.
"""

import csv
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = BASE / "similarity-ranking.csv"
CSV_SRC = Path(os.environ.get("COMPANIES_CSV", BASE / "universe.csv"))
OUT = BASE / "similarity-ranking-reachable.csv"

HEADCOUNT_LIMIT = 150

# name -> (reason code, one-line note)
REMOVE = {
    # hyperscalers
    "Alibaba Cloud":       ("hyperscaler", "global cloud division"),
    "Amazon Web Services": ("hyperscaler", "global cloud division"),
    "Google Cloud":        ("hyperscaler", "global cloud division, also a supplier"),
    "HUAWEI CLOUD":        ("hyperscaler", "global cloud division"),
    "IBM Cloud":           ("hyperscaler", "global cloud division"),
    "Oracle Cloud":        ("hyperscaler", "global cloud division"),
    "Cloudflare":          ("large network", "public company, edge network"),
    # large SaaS and platforms
    "Stripe":              ("large fintech", "public-scale payments company"),
    "MongoDB":             ("public company", "listed database vendor"),
    "Supabase":            ("late-stage platform", "large open-source platform"),
    "Vercel":              ("late-stage platform", "large developer platform"),
    "Zapier":              ("large SaaS", "automation leader"),
    "LaunchDarkly":        ("late-stage SaaS", "feature-flag leader"),
    "Pinecone":            ("late-stage SaaS", "vector DB leader"),
    "Neon":                ("late-stage SaaS", "acquired-scale database vendor"),
    "Telnyx":              ("large carrier", "global carrier"),
    "Deepgram":            ("late-stage AI", "voice AI leader"),
    "Resend":              ("late-stage SaaS", "email platform"),
    "Hostinger":           ("large host", "global hosting group"),
    "Render":              ("late-stage SaaS", "hosting platform"),
    "Replit":              ("late-stage SaaS", "large dev platform"),
    "Modal":               ("late-stage AI", "compute platform"),
    "Certora":             ("late-stage", "security vendor"),
    "Storj":               ("token-listed", "listed storage network"),
    # AI majors
    "OpenAI":              ("AI major", "frontier model lab"),
    "Anthropic":           ("AI major", "frontier model lab"),
    "Perplexity":          ("AI major", "consumer search brand"),
    "Replicate":           ("AI major", "model hosting leader"),
    "DeepSeek":            ("AI major", "frontier model lab"),
    # crypto majors and exchange divisions
    "Coinbase Cloud":      ("exchange division", "division of a listed exchange"),
    "CoinGecko":           ("category leader", "market-data leader"),
    "Etherscan":           ("category leader", "explorer leader"),
    "Alchemy":             ("headcount 373", "large infrastructure vendor"),
    "QuickNode":           ("headcount 110", "large RPC vendor"),
    "Infura":              ("corporate product", "product of ConsenSys"),
    "Blockdaemon":         ("headcount 210", "large node vendor"),
    "Nansen":              ("headcount 117", "large analytics vendor"),
    "Dune":                ("headcount 152", "large analytics vendor"),
    "Kaiko":               ("headcount 224", "market-data vendor"),
    "MoonPay":             ("large fintech", "fiat onramp leader"),
    "Transak":             ("large fintech", "fiat onramp vendor"),
    "Ramp Network":        ("large fintech", "fiat onramp vendor"),
    "0x":                  ("large protocol", "liquidity protocol company"),
    "Safe":                ("large foundation", "wallet standard, foundation-run"),
    "Privy":               ("acquired", "acquired by Stripe"),
    "Turnkey":             ("late-stage", "wallet infrastructure vendor"),
    "ChainUp Cloud":       ("headcount 120", "part of a large group"),
    "Zeeve":               ("headcount 120", "managed infra vendor"),
    "IntellectEU":         ("headcount 222", "large integrator"),
    # excluded by request: direct competitors, kept off the outreach list
    "Firecrawl":           ("competitor", "web data competitor, excluded by request"),
    "Apify":               ("competitor", "catalogue competitor and supplier, excluded by request"),
    "Exa":                 ("competitor", "web search competitor, excluded by request"),
}

# companies that already supply a route to usebuy: not outreach prospects
SUPPLIERS = {
    "Chainstack": "supplies the Celo RPC route",
    "SQD": "supplies the free multi-chain data route",
    "Google Cloud": "supplies the VM route",
}


def main():
    rank = list(csv.DictReader(open(SRC)))
    src = {r["company"]: r for r in csv.DictReader(open(CSV_SRC, encoding="utf-8-sig"))}

    kept, removed = [], []
    for r in rank:
        name = r["company"]
        hc_raw = src[name]["directory_headcount"].strip()
        hc = int(hc_raw) if hc_raw.isdigit() else None

        reason = None
        if name in REMOVE:
            reason = REMOVE[name]
        elif hc is not None and hc >= HEADCOUNT_LIMIT:
            reason = (f"headcount {hc}", "above the size limit")

        if reason:
            removed.append({**r, "headcount": hc_raw or "", "reason_code": reason[0], "reason": reason[1]})
        else:
            kept.append({**r, "headcount": hc_raw or "",
                         "size_band": ("small" if hc is not None and hc < 50 else
                                       "mid" if hc is not None else "unknown"),
                         "supplier": SUPPLIERS.get(name, "")})

    for i, r in enumerate(kept, 1):
        r["new_rank"] = i
        r["old_rank"] = r["rank"]

    fields = ["new_rank", "old_rank", "company", "url", "segment", "category", "score",
              "match_index", "capability_match", "core_hits", "tier", "headcount",
              "size_band", "supplier", "matched_capabilities", "services", "pricing_route"]
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(kept)

    rem_out = OUT.with_name("similarity-ranking-removed.csv")
    with open(rem_out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["old_rank", "company", "score", "category",
                                          "headcount", "reason_code", "reason"],
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(removed, key=lambda r: -float(r["score"])))

    print(f"kept {len(kept)}  removed {len(removed)}  total {len(kept) + len(removed)}")
    print(f"\nwrote {OUT}")
    print(f"wrote {rem_out}")
    print(f"\n{'#':>3} {'company':22s} {'score':>5} {'old':>4} {'hc':>4}  matched")
    for r in kept[:20]:
        print(f"{r['new_rank']:3d} {r['company'][:22]:22s} {r['score']:>5} {r['old_rank']:>4} "
              f"{r['headcount'] or '-':>4}  {r['matched_capabilities'][:60]}")


if __name__ == "__main__":
    main()
