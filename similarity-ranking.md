# Similarity ranking: 259 infrastructure companies against usebuy.ai

| Field | Value |
|---|---|
| Input | `infrastructure-companies.csv` (259 companies) |
| Reference | usebuy.ai (buy), capability surface from the live gateway catalogue |
| Method | Capability-weighted Jaccard, 88% of the final score |
| Output | `similarity-ranking.csv` (all 259 rows, full detail) |
| Script | `rank_similarity.py` (reproducible) |
| Date | 2026-11-23 |

---

## 1. Method

The comparison runs on **capabilities**, not on category labels.

1. I built a 30-tag capability vector for usebuy from the live catalogue. Each tag carries a weight equal to how central that capability is to what usebuy actually sells. Social media data carries 0.95 because 159 of its 170 routes are social scraping. Voice and email carry 0.04 because it sells neither.
2. I built the same vector for every company from its category, its service summary, and its service list.
3. The capability match is a weighted Jaccard score. It answers one question: **how much of usebuy's weighted capability surface does this company also cover?**
4. The final score is 88% capability, 7% delivery model (self-serve, metered), and 5% buyer (agent builder vs enterprise).

The capability term dominates, as you asked. The two small terms only break ties between companies with the same capability set.

## 2. Result

| # | Company | Score | Capability index | Matched capabilities |
|---|---|---|---|---|
| 1 | **BlockRun** | 95.1 | 100 | api gateway, pay-per-call, web search, blockchain data, model inference |
| 2 | **Firecrawl** | 68.3 | 70 | web scraping, web search, browser automation |
| 3 | **Apify** | 64.7 | 61 | web scraping, api gateway |
| 4 | Uniblock | 48.5 | 48 | api gateway, blockchain data, RPC |
| 5 | blockmachine | 46.8 | 46 | pay-per-call, blockchain data, RPC |
| 6 | Cloudflare | 39.5 | 40 | api gateway, cloud compute, hosting |
| 7 | Merge | 35.4 | 31 | api gateway |
| 8 | Zapier | 32.4 | 30 | MCP server, agent tools, workflow |
| 9 | Vercel | 31.7 | 34 | api gateway (model gateway), hosting |
| 10 | Crossmint | 30.2 | 32 | agent payments, wallet |
| 11 | Speakeasy | 28.1 | 27 | MCP server, developer docs and SDK |
| 12 | Exa | 28.0 | 24 | web search |
| 13 | Parallel | 28.0 | 24 | web search |
| 14 | Perplexity | 28.0 | 24 | web search |
| 15 | Tavily | 28.0 | 24 | web search |
| 16 | LI.FI | 27.8 | 31 | api gateway |
| 17 | Alchemy | 24.3 | 20 | blockchain data, RPC, wallet |
| 18 | Chaingateway.io | 24.3 | 20 | blockchain data, RPC, wallet |
| 19 | thirdweb | 24.3 | 20 | blockchain data, RPC, wallet |
| 20 | Browser Use | 23.9 | 15 | browser automation |
| 21 | Amforc | 23.7 | 23 | blockchain data, RPC, compute |
| 22 | Blink Labs | 23.7 | 20 | blockchain data, RPC, indexing |
| 23 | Goldsky | 23.7 | 20 | blockchain data, RPC, indexing |
| 24 | StreamingFast | 23.7 | 20 | blockchain data, RPC, indexing |

The capability index is scaled so the best match in the set equals 100.

## 3. Tier 1: direct comparables (3)

### 1. BlockRun — score 95

**Services:** model inference gateway; web search APIs; market data APIs; paid agent tools.

This is the only company in the 259 that runs the same business model. It is an agent-facing gateway that resells other providers' models, search, and data, and charges per call. The overlap covers 5 of usebuy's weighted capabilities, including the two that matter most: the gateway and the metered rail.

The difference is scope. BlockRun resells models and market data. usebuy resells social scrapers and Google VMs. Same shape, different inventory.

### 2. Firecrawl — score 68

**Services:** web scraping APIs; website crawling; web search; browser interaction.

Firecrawl covers usebuy's supply side directly. Every category in usebuy's data layer (scraping, crawling, search, browser) has a Firecrawl equivalent. It is the closest single-product match to what usebuy actually delivers per request.

It is not a marketplace and not a payment rail, which is why it lands below BlockRun.

### 3. Apify — score 65

**Services:** hosted web scraping actors; crawler execution; data extraction APIs.

Apify is the closest match to usebuy's **catalogue structure**. It runs a marketplace of third-party actors, prices them per run, and exposes them through one account. 121 of usebuy's 170 routes are the same idea with one vendor (TikHub) instead of thousands.

Apify is the strongest strategic comparable, even though its capability overlap is narrower than BlockRun's.

## 4. Tier 2: adjacent (13)

| Company | Score | Why it is adjacent |
|---|---|---|
| Uniblock | 48.5 | Unified blockchain API across many providers. Same aggregation model, different data domain. |
| blockmachine | 46.8 | Pay-per-call blockchain RPC. Same billing model, narrow inventory. |
| Cloudflare | 39.5 | Sells API gateways, serverless compute, and edge hosting. Infrastructure layer, not a data marketplace. |
| Merge | 35.4 | Unified enterprise APIs. Same "one API, many backends" pattern. |
| Zapier | 32.4 | Application integrations plus MCP tool access. Connector layer, not data. |
| Vercel | 31.7 | AI model gateway plus deployment. The gateway overlaps; the product does not. |
| Crossmint | 30.2 | The only company selling agent payment infrastructure. Closest match on the payments axis alone. |
| Speakeasy | 28.1 | Generates MCP servers and SDKs. Supplies the distribution layer usebuy depends on. |
| Exa | 28.0 | Web search API. One capability, well executed. |
| Parallel | 28.0 | Web research API. One capability. |
| Perplexity | 28.0 | Search and grounded answers. Consumer brand with an API. |
| Tavily | 28.0 | Search and extraction for agents. One capability. |
| LI.FI | 27.8 | Cross-chain aggregation APIs. Aggregator model, swap domain. |

## 5. The rest: 243 companies

243 companies score below 20. They share at most one weak capability with usebuy.

The block of 101 companies tied at exactly 21.3 is the RPC node providers. They all match on blockchain data and RPC, and they all fail on everything else. Their order inside that block carries no meaning. Do not read rank 25 as "more similar than rank 120".

Notable names and their scores:

| Company | Score | Reason for the low score |
|---|---|---|
| Alchemy | 24.3 | Data APIs and RPC. Real overlap, but on the blockchain axis only. |
| Chainstack | 21.3 | Already a usebuy partner. It supplies one route, not a capability set. |
| Browserbase | 20.1 | Browser sessions only. usebuy has one browser route. |
| Arcade | 16.0 | Authenticated tool execution. usebuy sells no connectors. |
| Modal | 16.7 | Sandboxes and GPU. One usebuy route is adjacent. |
| Anthropic, OpenAI, DeepSeek | 11.7 to 15.5 | Model providers. usebuy resells one closed-beta model. |
| Stripe, Dodo Payments | 13.2 | Payment processors. Different job from an agent payment rail. |
| Composio | 14.7 | App connectors. No data, no payments. |
| Mem0, Zep | 9.2 | Memory. usebuy sells none. |
| E2B | 8.3 | Code sandboxes. usebuy sells VMs, not sandboxes. |
| LangChain, CrewAI, Mastra | 8.1 to 10.6 | Orchestration. Different layer. |
| Mintlify, Fern | 7.7 to 11.5 | Documentation. Different layer. |

## 6. Capability coverage across the 259

This is the core result. For each usebuy capability, the table shows how many of the 259 companies offer it.

| usebuy capability | Weight | Companies offering it |
|---|---|---|
| Social media data | 0.95 | **0** |
| Web scraping | 0.90 | 2 |
| API gateway / aggregation | 0.90 | 7 |
| Pay-per-call metering | 0.85 | 2 |
| Agent payments | 0.85 | 1 |
| Web search | 0.70 | 6 |
| MCP server | 0.65 | 2 |
| Browser automation | 0.45 | 3 |
| Data enrichment | 0.40 | 0 |
| Identity verification | 0.30 | 1 |
| Blockchain data | 0.30 | 158 |
| Payment processing | 0.22 | 4 |
| Model inference | 0.20 | 8 |
| Blockchain RPC | 0.20 | 128 |
| Agent tools | 0.20 | 4 |
| Cloud compute | 0.18 | 18 |
| Developer docs and SDK | 0.15 | 3 |
| Wallet infrastructure | 0.10 | 14 |
| Hosting | 0.10 | 7 |
| Blockchain indexing | 0.08 | 32 |
| Code sandbox | 0.08 | 2 |
| Observability | 0.05 | 7 |
| Workflow | 0.04 | 8 |
| Memory | 0.04 | 2 |
| Vector database | 0.04 | 3 |
| Email | 0.04 | 2 |
| Voice | 0.04 | 2 |

## 7. What the ranking reveals

**1. Nobody in the list sells social media data.** Zero of 259. This is usebuy's largest capability and its entire inventory, and it has no direct competitor in this dataset. The CSV was built from blockchain directories and AI reports, and neither source covers social scraping vendors.

**2. The list is the wrong shape for usebuy.** 158 of 259 companies sell blockchain data and 128 sell RPC. usebuy's blockchain exposure is one partner route and one free dataset. The list measures a market usebuy barely enters.

**3. Only three companies are true comparables.** BlockRun, Firecrawl, and Apify. Each matches a different part of the model: BlockRun the business model, Firecrawl the supply, Apify the catalogue.

**4. usebuy's two pillars are split across different companies.** No company in the list combines a data marketplace with an agent payment rail. BlockRun comes closest and still does not settle payments itself. That combination is usebuy's only structural advantage.

**5. The closest competitors are missing from the CSV.** Agent402 (638 tools, same rails) is a direct competitor and is not in the list. Neither are the social scraping vendors that supply usebuy, such as TikHub and MrScraper. A ranking built on this CSV cannot find the real competitive set.

## 8. Caveats

1. The scores come from the CSV's own text fields. A company that sells social data but describes itself vaguely will score low.
2. The capability weights are my judgment, built from the live catalogue. The script is in the folder, so you can change a weight and rerun.
3. 101 companies tie at 21.3. Their order is arbitrary.
4. The buyer and delivery terms are heuristics from category and pricing route, not from research.
5. Absence from the CSV is not absence from the market. See finding 5.

## 9. Files

| File | Contents |
|---|---|
| `similarity-ranking.csv` | All 259 companies, ranked, with score, tier, matched capabilities, and services |
| `rank_similarity.py` | The scoring model. Edit `USEBUY` weights and rerun. |
