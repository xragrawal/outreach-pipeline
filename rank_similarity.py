#!/usr/bin/env python3
"""Rank the infrastructure CSV by similarity to usebuy.ai, weighted on capabilities.

Model
-----
1. A capability vector is built for usebuy.ai from the live gateway catalogue.
2. A capability vector is built for every CSV company from its category,
   service summary, and service list.
3. Capability match = weighted Jaccard over the two vectors, using the usebuy
   weight of each tag. This answers: how much of usebuy's weighted capability
   surface does this company also cover?
4. Two small tie-breakers are added: delivery model and buyer.

Final = 0.75 * capability + 0.15 * delivery + 0.10 * buyer
The capability term dominates, as requested.
"""

import csv, json, os, re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
CSV_PATH = Path(os.environ.get("COMPANIES_CSV", BASE / "universe.csv"))
OUT_DIR = BASE

# ---------------------------------------------------------------------------
# usebuy capability surface, from gateway /v1/catalog + docs + site
# weight = how central the capability is to what usebuy actually sells
# ---------------------------------------------------------------------------
USEBUY = {
    "social_media_data":      0.95,  # 159 of 170 routes are social scraping
    "web_scraping":           0.90,  # Apify/TikHub/MrScraper scraping
    "api_gateway":            0.90,  # gateway proxies third-party APIs
    "pay_per_call":           0.85,  # x402 metered billing per request
    "agent_payments":         0.85,  # stablecoin settlement, wallet, receipts
    "web_search":             0.70,  # x.posts.search, reddit.posts.search, Agent402 web tools
    "mcp_server":             0.65,  # buy mcp install, 8 tools
    "data_enrichment":        0.40,  # LinkedIn/email endpoints via ContactOut/Clay/Ploid
    "browser_automation":     0.45,  # 1 route: browser.sessions.create
    "identity_verification":  0.30,  # Self zk proofs, ERC-8004
    "blockchain_data":        0.30,  # SQD free route, multi-chain datasets
    "blockchain_indexing":    0.08,  # not sold; only consumed through SQD
    "model_inference":        0.20,  # 1 route: cencori, closed beta
    "cloud_compute":          0.18,  # 1 route: Google Cloud VMs
    "blockchain_rpc":         0.20,  # 1 route: Chainstack Celo
    "payments_processing":    0.22,  # it is a rail, not a PSP
    "dev_docs_sdk":           0.15,  # docs, CLI, npm packages
    "code_sandbox":           0.08,
    "wallet_infra":           0.10,  # CLI keystore only
    "observability":          0.05,
    "memory":                 0.04,
    "vector_db":              0.04,
    "workflow":               0.04,
    "email_infra":            0.04,
    "voice_infra":            0.04,
    "agent_orchestration":    0.05,
    "hosting":                0.10,
    "fiat_onramp":            0.05,
    "feature_flags":          0.02,
    "authorization":          0.05,
    "agent_tools":            0.20,  # connectors/auth for agents
}

# ---------------------------------------------------------------------------
# tagging rules: (tag, regex) applied to lowercased category|summary|services
# ---------------------------------------------------------------------------
RULES = [
    ("social_media_data", r"\bsocial (data|media|post)|tiktok|instagram|linkedin data|x posts"),
    ("web_scraping",      r"scrap|crawl|data extraction"),
    ("web_search",        r"web search|search api|search and grounded|grounded answer|web research"),
    ("data_enrichment",   r"enrich|contactout|people data|work email|email finder"),
    ("browser_automation",r"browser session|browser automation|browser interaction|browser execution|cloud browser"),
    ("api_gateway",       r"api gateway|model gateway|unified (enterprise |blockchain )?api|aggregat|marketplace|hosted .*actors|gateway for|single api"),
    ("pay_per_call",      r"per request|usage-based|usage based|pay-per-call|pay per call|metered|paid access|usage-priced"),
    ("agent_payments",    r"x402|agent payment|agentic payment|payment infrastructure for agents"),
    ("mcp_server",        r"\bmcp\b"),
    ("identity_verification", r"identity verification|\bkyc\b|attestation|proof of person|zk proof"),
    ("blockchain_data",   r"blockchain data|indexed blockchain|explorer api|market data api|token market|wallet data|transaction data|blockchain api"),
    ("blockchain_rpc",    r"\brpc\b"),
    ("blockchain_indexing", r"indexing|indexer"),
    ("model_inference",   r"model inference|inference api|generation api|language model|hosted model"),
    ("cloud_compute",     r"serverless compute|virtual machine|\bvm\b|gpu|cloud compute|bare-metal|dedicated server|cloud server"),
    ("payments_processing", r"payment processing|billing|subscription billing|checkout|financial infrastructure"),
    ("wallet_infra",      r"embedded wallet|smart account|key management|multisig|account abstraction|wallet api|wallet infrastructure"),
    ("email_infra",       r"email sending|transactional email|email inbox|email delivery"),
    ("voice_infra",       r"speech|voice api|voice agent|telecommunication"),
    ("memory",            r"agent memory|persistent memory|context retrieval"),
    ("vector_db",         r"vector (database|search|similarity)|pgvector|embedding storage"),
    ("observability",     r"evaluation|evaluat|tracing|observability|experiment tracking"),
    ("code_sandbox",      r"sandbox"),
    ("workflow",          r"workflow|task queue|background job|durable execution"),
    ("dev_docs_sdk",      r"sdk generation|documentation hosting|developer portal|api documentation|agent-readable documentation"),
    ("agent_orchestration", r"orchestration|agent runtime|multi-agent|agent development platform"),
    ("hosting",           r"application hosting|web hosting|application deployment|app deployment|hosted development|deployment infrastructure|cloud hosting|managed application hosting"),
    ("fiat_onramp",       r"onramp|on-ramp|fiat"),
    ("feature_flags",     r"feature flag"),
    ("authorization",     r"authori[sz]ation|permission polic|access control"),
    ("agent_tools",       r"tool execution|authenticated tool|tool access|agent authorization|agent security"),
]

# buyer / delivery heuristics
AGENT_BUYER_CATEGORIES = {
    "Web data infrastructure": 1.00,
    "Agent API gateway": 1.00,
    "Agent tools and authentication": 0.95,
    "Browser infrastructure": 0.90,
    "Agent memory": 0.85,
    "Agent observability": 0.85,
    "AI evaluation and observability": 0.80,
    "Agent runtime": 0.80,
    "Agent orchestration": 0.75,
    "Agent orchestration and observability": 0.75,
    "Code execution sandboxes": 0.75,
    "Model inference": 0.70,
    "API developer infrastructure": 0.65,
    "Workflow infrastructure": 0.60,
    "Email infrastructure": 0.55,
    "Voice infrastructure": 0.55,
    "Payment infrastructure": 0.55,
    "Agent security": 0.55,
    "Database infrastructure": 0.45,
    "Cloud compute": 0.45,
    "Cloud hosting": 0.35,
    "Cloud development infrastructure": 0.40,
    "Developer infrastructure": 0.40,
    "Authorization infrastructure": 0.35,
    "Identity infrastructure": 0.35,
    "Wallet infrastructure": 0.35,
    "Wallet and payment infrastructure": 0.40,
    "Blockchain data infrastructure": 0.35,
    "Blockchain data APIs": 0.35,
    "Blockchain RPC and data APIs": 0.25,
    "Transaction infrastructure": 0.25,
    "Trading API infrastructure": 0.20,
    "Cross-chain API infrastructure": 0.20,
    "Storage infrastructure": 0.20,
    "Cloud and blockchain infrastructure": 0.20,
    "Cloud compute and hosting": 0.30,
    "Cloud compute and storage": 0.30,
    "Managed blockchain infrastructure": 0.20,
    "Blockchain security infrastructure": 0.15,
}

METERED_CATEGORIES = {"Web data infrastructure", "Agent API gateway", "Model inference", "Blockchain data infrastructure",
                      "Blockchain data APIs", "Blockchain RPC and data APIs", "Browser infrastructure", "Code execution sandboxes"}

# capabilities that define usebuy's core business, used for the tier rule
CORE_TAGS = {"social_media_data", "web_scraping", "api_gateway", "pay_per_call",
             "agent_payments", "web_search", "mcp_server"}


def tag_company(row):
    text = " | ".join([row["infrastructure_category"], row["service_summary"], row["infra_services_sold"]]).lower()
    tags = set()
    for tag, pat in RULES:
        if re.search(pat, text):
            tags.add(tag)
    # guard: "email" alone must not become email_infra
    if "email" in text and re.search(r"email (sending|delivery|inbox|api)", text):
        tags.add("email_infra")
    # guard: observability only in an AI context
    if "observability" in tags and not re.search(r"agent|model|prompt|llm", text):
        tags.discard("observability")
    return tags


def wjaccard(a, b, weights):
    inter = sum(weights[t] for t in (a & b))
    union = sum(weights[t] for t in (a | b))
    return inter / union if union else 0.0


def delivery_score(row):
    s = 0.0
    if row["sales_route"].startswith("Published pricing"):
        s += 0.45                                   # self-serve, price on the site
    if row["infrastructure_category"] in METERED_CATEGORIES:
        s += 0.30                                   # usage-based or per-call
    if re.search(r"\bmcp\b", row["infra_services_sold"], re.I):
        s += 0.15
    if row["commercial_evidence_type"] == "company_service_page":
        s += 0.10
    return min(s, 1.0)


def main():
    rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8-sig")))
    ub = set(USEBUY)
    results = []
    for r in rows:
        tags = tag_company(r)
        cap = wjaccard(ub, tags, USEBUY)
        dlv = delivery_score(r)
        byr = AGENT_BUYER_CATEGORIES.get(r["infrastructure_category"], 0.25)
        matched = sorted((t for t in (ub & tags)), key=lambda t: -USEBUY[t])
        results.append({
            "company": r["company"],
            "url": r["url"],
            "segment": r["segment"],
            "category": r["infrastructure_category"],
            "capability_match": round(cap * 100, 1),
            "delivery": round(dlv * 100, 1),
            "buyer": round(byr * 100, 1),
            "matched_capabilities": "; ".join(matched),
            "services": r["infra_services_sold"],
            "pricing_route": r["sales_route"],
        })

    best = max(r["capability_match"] for r in results)
    for r in results:
        r["match_index"] = round(r["capability_match"] / best * 100, 1) if best else 0
        # capability carries 88% of the final score; the tie-breakers add at most 12 points
        r["score"] = round(0.88 * r["match_index"] + 0.07 * r["delivery"] + 0.05 * r["buyer"], 1)
        core = sum(1 for t in r["matched_capabilities"].split("; ") if t in CORE_TAGS)
        r["core_hits"] = core
        if r["match_index"] >= 55 and core >= 2:
            r["tier"] = "1 direct"
        elif r["match_index"] >= 18 and core >= 1:
            r["tier"] = "2 adjacent"
        else:
            r["tier"] = "3 different layer"

    results.sort(key=lambda r: (-r["score"], -r["capability_match"], -r["core_hits"], r["company"].lower()))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "similarity-ranking.csv"
    fields = ["rank", "tier", "company", "url", "segment", "category", "score", "match_index",
              "capability_match", "core_hits", "delivery", "buyer", "matched_capabilities", "services", "pricing_route"]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for i, r in enumerate(results, 1):
            r["rank"] = i
            w.writerow(r)

    print(f"wrote {out}")
    print(f"{'#':>3} {'company':22s} {'score':>6} {'cap':>6} {'idx':>5}  matched")
    for r in results[:40]:
        print(f"{r['rank']:3d} {r['company'][:22]:22s} {r['score']:6.1f} {r['capability_match']:6.1f} {r['match_index']:5.0f}  {r['matched_capabilities'][:70]}")


if __name__ == "__main__":
    main()
