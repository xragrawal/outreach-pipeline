# ICP: companies similar to useBuy.ai

| Field | Value |
|---|---|
| Subject | useBuy.ai |
| Use of this file | Stage 1 output. It defines who counts as a match and what each match is scored on. |
| Date | 2026-11-24 |
| Evidence base | Live gateway catalogue, docs, and site, read 2026-11-23 |

---

## Buyer

| Field | Value |
|---|---|
| Who | An AI agent with a funded wallet, or a developer who wires agents |
| What they need | Live web and social data, one call at a time |
| How they pay | Per request, in USDC, USDT, or USAT on Celo |
| What they refuse | A monthly minimum, a card on file, a separate key per vendor |
| Volume pattern | Spiky. Ten calls one week, ten thousand the next. |

The buyer is not a procurement team. The buyer is code. That shapes the ICP: a matching company must sell a callable endpoint, not a contract.

## Value proposition

One key, one balance, and 170 routes. The agent pays per call and gets a result.

Three parts hold this up:

1. **Catalogue breadth.** 170 routes across social data, scraping, search, and data APIs.
2. **Metering.** x402 v1 and v2, per-request pricing, receipts.
3. **Settlement.** Stablecoins on Celo, with ERC-8004 identity and reputation.

## Capability surface

31 capabilities, taken from the live catalogue. Each one carries a weight. The weight is how central the capability is to what useBuy actually sells, not how often the word appears.

| Rank | Capability | Weight | Why |
|---|---|---|---|
| 1 | Social media data | 0.95 | 165 of 170 routes |
| 2 | Web scraping | 0.90 | Apify, TikHub, MrScraper inventory |
| 3 | API gateway | 0.90 | The product is a proxy |
| 4 | Pay per call | 0.85 | The billing model |
| 5 | Agent payments | 0.85 | Stablecoin settlement and receipts |
| 6 | Web search | 0.70 | 33 search routes |
| 7 | MCP server | 0.65 | 8 tools, installable |
| 8 | Browser automation | 0.45 | One route |
| 9 | Data enrichment | 0.40 | ContactOut, Clay, Ploid |
| 10 | Identity verification | 0.30 | Self zk proofs, ERC-8004 |

The full 31-row table is `pipeline/taxonomy.csv`. It holds the weight, the core flag, and the regex that detects the tag.

Weight sum: **9.18**.

## Weights

The final score uses three terms.

| Term | Weight | What it measures |
|---|---|---|
| Capability | 0.88 | How much of the weighted capability surface the company also covers |
| Delivery | 0.07 | Whether it sells the same way: API, metered, self-serve |
| Buyer | 0.05 | Whether it sells to the same buyer: agents and developers |

Capability dominates on purpose. Two companies can both sell an API and still be poor matches.

Capability match is a weighted Jaccard score. It is then rescaled so the best company in the universe scores 100.

## Core capabilities

Seven tags decide whether a company is in the same business or only nearby.

| Core tag | Weight |
|---|---|
| `social_media_data` | 0.95 |
| `web_scraping` | 0.90 |
| `api_gateway` | 0.90 |
| `pay_per_call` | 0.85 |
| `agent_payments` | 0.85 |
| `web_search` | 0.70 |
| `mcp_server` | 0.65 |

A company with a high score but no core hit is a false positive. The tier rule catches this.

| Tier | Rule |
|---|---|
| 1 | match index 55 or more, and 2 or more core hits |
| 2 | match index 18 or more, and 1 or more core hit |
| 3 | everything else |

## Anti-ICP

These are excluded before scoring, or removed after it.

| Group | Why | Examples |
|---|---|---|
| Hyperscalers | No reachable owner for one product line | AWS, Google Cloud, Oracle, IBM, Alibaba |
| Model labs | Sell one capability, at frontier scale | OpenAI, Anthropic, DeepSeek |
| Single-layer RPC | Same three tags, one product, no breadth | The 98-row node-hosting block |
| Direct competitors | They are the product, not a partner | Firecrawl, Apify, Exa |
| Large public vendors | Sales cycle too long for a per-call deal | Stripe, MongoDB, Cloudflare |

Size limit: headcount 150 or more is removed.

The anti-ICP matters as much as the ICP. Without it the ranking fills with companies that look similar on paper and cannot be sold to.

## Evidence

| Source | URL | Read |
|---|---|---|
| Gateway catalogue | https://gateway.usebuy.ai/v1/catalog | 2026-11-23 |
| Pricing and routes | Gateway `priceOptions` fields | 2026-11-23 |
| Company profile | `company-profile.md` | 2026-11-23 |
| Service analysis | `service-catalogue-analysis.md` | 2026-11-23 |

## What this ICP does not cover

| Gap | Effect |
|---|---|
| No revenue data | Cannot weight by deal size |
| No buyer-company size | Cannot target by account value |
| No geography | Cannot filter by region |
| No intent signal | Cannot tell who is buying now |

A later version should add these four fields. Each one needs a paid source.
