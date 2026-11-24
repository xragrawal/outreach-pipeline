# Full scoring table

| Field | Value |
|---|---|
| Total companies scored | 259 |
| Kept (reachable) | 207 |
| Removed | 52 |
| Final score range | 0 to 100 |
| Model file | `taxonomy.csv` plus `run.json` |
| Filter file | `filter_reachable.py` |
| Date | 2026-11-23 |

---

# 1. How the score is generated

## 1.1 The formula

```
capability_match = sum(useBuy_weight[t] for t in shared) / sum(useBuy_weight[t] for t in either)
capability_index = capability_match / best_capability_match * 100
final_score      = 0.88 * capability_index + 0.07 * delivery + 0.05 * buyer
```

Three terms, in order of weight:

| Term | Weight | Question it answers |
|---|---|---|
| Capability index | 88% | How much of usebuy's weighted capability surface does this company also cover? |
| Delivery | 7% | Does it sell the same way: self-serve, published price, metered? |
| Buyer | 5% | Does it sell to the same buyer: agent builders and developers? |

The capability term dominates. The other two only separate companies that share the same capability set.

## 1.2 Step 1: the usebuy capability vector

This vector is the reference. Each weight is set from evidence in the live gateway catalogue, not from opinion. The total weight is 9.18.

| Capability | Weight | Evidence used to set the weight | Source |
|---|---|---|---|
| Social media data | 0.95 | 165 of 170 catalogue routes are on 6 social platforms (Instagram 35, TikTok 32, YouTube 32, LinkedIn 25, Reddit 22, X 19) | `/v1/catalog` |
| Web scraping | 0.90 | 161 of 170 routes come from 4 scraping vendors (TikHub 121, Apify 27, MrScraper 7, Ploid 6) | `/v1/catalog` |
| API gateway | 0.90 | One host resells 10 upstream providers behind one 402 handshake | `/v1/catalog`, `/docs` |
| Pay per call | 0.85 | Every route quotes a price per request. No subscription exists. | `/docs`, `/limits` |
| Agent payments | 0.85 | 3 stablecoins, 1 payTo address, EIP-3009 transfer signing, receipts | `/docs`, `/v1/catalog` |
| Web search | 0.70 | 33 of 170 routes are search endpoints. 3 are curated (`x.posts.search`, `reddit.posts.search`, `youtube.videos.search`) | `/v1/catalog` |
| MCP server | 0.65 | 8 tools registered over stdio for Claude Code and Codex | `/docs` |
| Browser automation | 0.45 | 1 route (`browser.sessions.create`), 5 price points from $0.0036 to $0.0091 | `/v1/catalog` |
| Data enrichment | 0.40 | 5 routes return person or contact data (ContactOut 2, Clay 1, Ploid 1, Apify 1) | `/v1/catalog` |
| Identity verification | 0.30 | Self.xyz zero-knowledge proofs, ERC-8004 identity and reputation registries | `/docs`, `/v1/catalog` |
| Blockchain data | 0.30 | 1 free route (SQD Portal), 7 endpoints across 100+ chains | `/v1/catalog`, `/limits` |
| Payments processing | 0.22 | It settles payments but is not a card processor or merchant of record | `/docs` |
| Blockchain RPC | 0.20 | 1 route (Chainstack Celo), $0.01 per request | `/v1/catalog` |
| Agent tools | 0.20 | No connector layer. Only MCP exposure of its own routes. | `/v1/catalog` |
| Model inference | 0.20 | 1 route (Cencori), one model, closed beta | `/v1/catalog` |
| Cloud compute | 0.18 | 1 route (Google Cloud VM), 6 sizes, $0.0168 to $0.5361 per hour | `/docs`, `/limits` |
| Developer docs and SDK | 0.15 | 3 site pages, a CLI, and 8 npm packages under `@celo/buy` | site, npm registry |
| Hosting | 0.10 | Sells VMs, not application hosting | `/docs` |
| Wallet infrastructure | 0.10 | CLI keystore only. No wallet product. | npm, `/docs` |
| Blockchain indexing | 0.08 | Consumes SQD data, does not sell an indexer | `/v1/catalog` |
| Code sandbox | 0.08 | VMs only, no sandbox API | `/docs` |
| Agent orchestration | 0.05 | None sold | `/v1/catalog` |
| Observability | 0.05 | None sold | `/v1/catalog` |
| Memory | 0.04 | None sold | `/v1/catalog` |
| Vector database | 0.04 | None sold | `/v1/catalog` |
| Workflow | 0.04 | None sold | `/v1/catalog` |
| Email | 0.04 | None sold | `/v1/catalog` |
| Voice | 0.04 | None sold | `/v1/catalog` |
| Authorization | 0.05 | None sold beyond payment authorization | `/v1/catalog` |
| Fiat onramp | 0.05 | None sold | `/v1/catalog` |
| Feature flags | 0.02 | None sold | `/v1/catalog` |

## 1.3 Step 2: tagging each company

Each of the 259 companies gets a set of capability tags. The tags come from three CSV columns, never from outside knowledge:

- `infrastructure_category`
- `service_summary`
- `infra_services_sold`

The text is lowercased and joined. A tag is added when its rule matches.

| # | Tag | Rule (regular expression) |
|---|---|---|
| 1 | `social_media_data` | `\bsocial (data\|media\|post)\|tiktok\|instagram\|linkedin data\|x posts` |
| 2 | `web_scraping` | `scrap\|crawl\|data extraction` |
| 3 | `web_search` | `web search\|search api\|search and grounded\|grounded answer\|web research` |
| 4 | `data_enrichment` | `enrich\|contactout\|people data\|work email\|email finder` |
| 5 | `browser_automation` | `browser session\|browser automation\|browser interaction\|browser execution\|cloud browser` |
| 6 | `api_gateway` | `api gateway\|model gateway\|unified (enterprise \|blockchain )?api\|aggregat\|marketplace\|hosted .*actors\|gateway for\|single api` |
| 7 | `pay_per_call` | `per request\|usage-based\|usage based\|pay-per-call\|pay per call\|metered\|paid access\|usage-priced` |
| 8 | `agent_payments` | `x402\|agent payment\|agentic payment\|payment infrastructure for agents` |
| 9 | `mcp_server` | `\bmcp\b` |
| 10 | `identity_verification` | `identity verification\|\bkyc\b\|attestation\|proof of person\|zk proof` |
| 11 | `blockchain_data` | `blockchain data\|indexed blockchain\|explorer api\|market data api\|token market\|wallet data\|transaction data\|blockchain api` |
| 12 | `blockchain_rpc` | `\brpc\b` |
| 13 | `blockchain_indexing` | `indexing\|indexer` |
| 14 | `model_inference` | `model inference\|inference api\|generation api\|language model\|hosted model` |
| 15 | `cloud_compute` | `serverless compute\|virtual machine\|\bvm\b\|gpu\|cloud compute\|bare-metal\|dedicated server\|cloud server` |
| 16 | `payments_processing` | `payment processing\|billing\|subscription billing\|checkout\|financial infrastructure` |
| 17 | `wallet_infra` | `embedded wallet\|smart account\|key management\|multisig\|account abstraction\|wallet api\|wallet infrastructure` |
| 18 | `email_infra` | `email sending\|transactional email\|email inbox\|email delivery` |
| 19 | `voice_infra` | `speech\|voice api\|voice agent\|telecommunication` |
| 20 | `memory` | `agent memory\|persistent memory\|context retrieval` |
| 21 | `vector_db` | `vector (database\|search\|similarity)\|pgvector\|embedding storage` |
| 22 | `observability` | `evaluation\|evaluat\|tracing\|observability\|experiment tracking` |
| 23 | `code_sandbox` | `sandbox` |
| 24 | `workflow` | `workflow\|task queue\|background job\|durable execution` |
| 25 | `dev_docs_sdk` | `sdk generation\|documentation hosting\|developer portal\|api documentation\|agent-readable documentation` |
| 26 | `agent_orchestration` | `orchestration\|agent runtime\|multi-agent\|agent development platform` |
| 27 | `hosting` | `application hosting\|web hosting\|application deployment\|app deployment\|hosted development\|deployment infrastructure\|cloud hosting\|managed application hosting` |
| 28 | `fiat_onramp` | `onramp\|on-ramp\|fiat` |
| 29 | `feature_flags` | `feature flag` |
| 30 | `authorization` | `authori[sz]ation\|permission polic\|access control` |
| 31 | `agent_tools` | `tool execution\|authenticated tool\|tool access\|agent authorization\|agent security` |

Two guards stop false positives:

1. `email` alone does not create `email_infra`. The text must name email sending, delivery, or an inbox.
2. `observability` is dropped unless the text also names an agent, model, prompt, or LLM. This stops RPC vendors from scoring on "transaction monitoring".

## 1.4 Step 3: the capability match

The match is a weighted Jaccard score over the two tag sets. Weights are the usebuy weights from 1.2.

```
intersection = sum of usebuy weights for tags in both sets
union        = sum of usebuy weights for tags in either set
match        = intersection / union
```

Because usebuy holds every tag in the model, the union is 9.18 for any company whose tags are a subset. A company with 3 tags is scored on those 3 weights divided by 9.18.

The index rescales the result so the best company equals 100. This keeps the number readable. It does not change the order.

## 1.5 Step 4: the delivery term

A simple additive score, capped at 1.0. It uses four CSV columns.

| Signal | Points | Exact test in the script |
|---|---|---|
| Published pricing on the site | +0.45 | `sales_route` starts with `Published pricing` |
| Category is metered or per-call | +0.30 | `infrastructure_category` is in `METERED_CATEGORIES` |
| MCP named in the service list | +0.15 | `\bmcp\b` matches `infra_services_sold` |
| Vendor page used as commercial proof | +0.10 | `commercial_evidence_type` equals `company_service_page` |

The sum is capped at 1.0. `METERED_CATEGORIES` holds 8 categories: Web data, Agent API gateway, Model inference, Blockchain data, Blockchain data APIs, Blockchain RPC and data APIs, Browser infrastructure, Code execution sandboxes.

## 1.6 Step 5: the buyer term

A lookup from `infrastructure_category`. The values encode how close the buyer is to an agent builder.

| `infrastructure_category` | Buyer value |
|---|---|
| Agent API gateway | 1.00 |
| Web data infrastructure | 1.00 |
| Agent tools and authentication | 0.95 |
| Browser infrastructure | 0.90 |
| Agent memory | 0.85 |
| Agent observability | 0.85 |
| AI evaluation and observability | 0.80 |
| Agent runtime | 0.80 |
| Agent orchestration | 0.75 |
| Agent orchestration and observability | 0.75 |
| Code execution sandboxes | 0.75 |
| Model inference | 0.70 |
| API developer infrastructure | 0.65 |
| Workflow infrastructure | 0.60 |
| Agent security | 0.55 |
| Email infrastructure | 0.55 |
| Payment infrastructure | 0.55 |
| Voice infrastructure | 0.55 |
| Cloud compute | 0.45 |
| Database infrastructure | 0.45 |
| Cloud development infrastructure | 0.40 |
| Developer infrastructure | 0.40 |
| Wallet and payment infrastructure | 0.40 |
| Authorization infrastructure | 0.35 |
| Blockchain data APIs | 0.35 |
| Blockchain data infrastructure | 0.35 |
| Cloud hosting | 0.35 |
| Identity infrastructure | 0.35 |
| Wallet infrastructure | 0.35 |
| Cloud compute and hosting | 0.30 |
| Cloud compute and storage | 0.30 |
| Blockchain RPC and data APIs | 0.25 |
| Transaction infrastructure | 0.25 |
| Cloud and blockchain infrastructure | 0.20 |
| Cross-chain API infrastructure | 0.20 |
| Managed blockchain infrastructure | 0.20 |
| Storage infrastructure | 0.20 |
| Trading API infrastructure | 0.20 |
| Blockchain security infrastructure | 0.15 |
| Any other category (default) | 0.25 |

## 1.7 Worked examples

**BlockRun, score 95.1.** Tags: api_gateway 0.90, pay_per_call 0.85, web_search 0.70, blockchain_data 0.30, model_inference 0.20. Intersection 2.95. Match 2.95 / 9.18 = 32.14%. It is the best match, so the index is 100. Delivery 0.30 (metered category, no published price). Buyer 1.00 (agent API gateway).
`0.88 × 100 + 0.07 × 30 + 0.05 × 100 = 95.1`

**Uniblock, score 48.5.** Tags: api_gateway 0.90, blockchain_data 0.30, blockchain_rpc 0.20. Intersection 1.40. Match 1.40 / 9.18 = 15.25%, stored as 15.3. Index 15.3 / 32.1 × 100 = 47.7. Delivery 0.75 (published price plus metered). Buyer 0.25 (RPC category).
`0.88 × 47.7 + 0.07 × 75 + 0.05 × 25 = 48.5`

The script rounds the match to one decimal before it divides by the best. This is why 15.25% becomes index 47.7, not 47.4.

**Crossmint, score 30.2.** Tags: agent_payments 0.85, wallet_infra 0.10. Intersection 0.95. Match 10.35%. Index 32.1. Delivery 0.00 (no published price, not a metered category). Buyer 0.40 (wallet and payment infrastructure).
`0.88 × 32.1 + 0.07 × 0 + 0.05 × 40 = 30.2`

**1RPC, score 21.3.** Tags: blockchain_data 0.30, blockchain_rpc 0.20. Intersection 0.50. Match 5.45%. Index 16.8. Delivery 0.75. Buyer 0.25.
`0.88 × 16.8 + 0.07 × 75 + 0.05 × 25 = 21.3`

This last example shows why 98 companies tie. Any company with only the blockchain data and RPC tags gets the same 21.3, because nothing else in the CSV separates them.

## 1.8 What the score is not

1. It is not a market-size or quality measure. It measures overlap with usebuy's capabilities.
2. It is not a prediction of fit for a partnership. A low score can still be a good supplier.
3. It depends on the CSV text. A company that sells social data but describes itself vaguely will score low. That is a limit of the input, not of the company.
4. The weights are a judgment call, set from the catalogue evidence in 1.2. Change a weight in `taxonomy.csv` and rerun to test a different view.
5. The buyer term is a category heuristic, not research.
6. 87 of the 207 kept companies have no headcount in the CSV. The `Staff` column shows an em dash for them. That is missing data, not a small company. Across all 259 rows, 127 have no headcount.

---

# 2. Kept list, 207 companies


| # | Company | Score | Cap index | Staff | Tier | Matched capabilities |
|---|---|---|---|---|---|---|
| 1 | BlockRun | 95.1 | 100.0 | — | 1 | api_gateway; pay_per_call; web_search; blockchain_data; model_inference |
| 2 | Uniblock | 48.5 | 47.7 | 16 | 2 | api_gateway; blockchain_data; blockchain_rpc |
| 3 | blockmachine | 46.8 | 45.8 | 1 | 2 | pay_per_call; blockchain_data; blockchain_rpc |
| 4 | Merge | 35.4 | 30.5 | — | 2 | api_gateway |
| 5 | Crossmint | 30.2 | 32.1 | — | 2 | agent_payments; wallet_infra |
| 6 | Speakeasy | 28.1 | 27.1 | — | 2 | mcp_server; dev_docs_sdk |
| 7 | Parallel | 28.0 | 23.7 | — | 2 | web_search |
| 8 | Tavily | 28.0 | 23.7 | — | 2 | web_search |
| 9 | LI.FI | 27.8 | 30.5 | — | 2 | api_gateway |
| 10 | Chaingateway.io | 24.3 | 20.2 | 2 | 3 | blockchain_data; blockchain_rpc; wallet_infra |
| 11 | thirdweb | 24.3 | 20.2 | 19 | 3 | blockchain_data; blockchain_rpc; wallet_infra |
| 12 | Browser Use | 23.9 | 15.3 | — | 3 | browser_automation |
| 13 | Amforc | 23.7 | 23.1 | 5 | 3 | blockchain_data; blockchain_rpc; cloud_compute |
| 14 | Blink Labs | 23.7 | 19.6 | 6 | 3 | blockchain_data; blockchain_rpc; blockchain_indexing |
| 15 | Goldsky | 23.7 | 19.6 | 30 | 3 | blockchain_data; blockchain_rpc; blockchain_indexing |
| 16 | StreamingFast | 23.7 | 19.6 | — | 3 | blockchain_data; blockchain_rpc; blockchain_indexing |
| 17 | 1RPC | 21.3 | 16.8 | 7 | 3 | blockchain_data; blockchain_rpc |
| 18 | 4EVERLAND | 21.3 | 16.8 | 5 | 3 | blockchain_data; blockchain_rpc |
| 19 | All That Node | 21.3 | 16.8 | 59 | 3 | blockchain_data; blockchain_rpc |
| 20 | Allnodes | 21.3 | 16.8 | 6 | 3 | blockchain_data; blockchain_rpc |
| 21 | Ankr | 21.3 | 16.8 | 87 | 3 | blockchain_data; blockchain_rpc |
| 22 | ARKHIA | 21.3 | 16.8 | 3 | 3 | blockchain_data; blockchain_rpc |
| 23 | Asternodes | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 24 | AvaCloud | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 25 | AZXA.IO | 21.3 | 16.8 | 4 | 3 | blockchain_data; blockchain_rpc |
| 26 | BitHub | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 27 | BLAZED.sh | 21.3 | 16.8 | 1 | 3 | blockchain_data; blockchain_rpc |
| 28 | BlazingNode | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 29 | BlockCypher | 21.3 | 16.8 | 1 | 3 | blockchain_data; blockchain_rpc |
| 30 | BlockEden.xyz | 21.3 | 16.8 | 1 | 3 | blockchain_data; blockchain_rpc |
| 31 | Blockfrost | 21.3 | 16.8 | 3 | 3 | blockchain_data; blockchain_rpc |
| 32 | Blockops | 21.3 | 16.8 | 9 | 3 | blockchain_data; blockchain_rpc |
| 33 | BlockPI | 21.3 | 16.8 | 5 | 3 | blockchain_data; blockchain_rpc |
| 34 | BlockReq | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 35 | BLOCKSIZE | 21.3 | 16.8 | 13 | 3 | blockchain_data; blockchain_rpc |
| 36 | BlockVectra | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 37 | BlockVision | 21.3 | 16.8 | 7 | 3 | blockchain_data; blockchain_rpc |
| 38 | Boar Network | 21.3 | 16.8 | 5 | 3 | blockchain_data; blockchain_rpc |
| 39 | BoltRPC | 21.3 | 16.8 | 3 | 3 | blockchain_data; blockchain_rpc |
| 40 | Canton Nodes | 21.3 | 16.8 | 5 | 3 | blockchain_data; blockchain_rpc |
| 41 | Chain.love | 21.3 | 16.8 | 6 | 3 | blockchain_data; blockchain_rpc |
| 42 | CHAINNODES | 21.3 | 16.8 | 10 | 3 | blockchain_data; blockchain_rpc |
| 43 | Chainstack | 21.3 | 16.8 | 55 | 3 | blockchain_data; blockchain_rpc |
| 44 | constant-k | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 45 | Corvus Labs | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 46 | Crypto APIs | 21.3 | 16.8 | 12 | 3 | blockchain_data; blockchain_rpc |
| 47 | DedicatedNodes.io | 21.3 | 16.8 | 1 | 3 | blockchain_data; blockchain_rpc |
| 48 | Demeter | 21.3 | 16.8 | 17 | 3 | blockchain_data; blockchain_rpc |
| 49 | dRPC | 21.3 | 16.8 | 19 | 3 | blockchain_data; blockchain_rpc |
| 50 | Dwellir | 21.3 | 16.8 | 10 | 3 | blockchain_data; blockchain_rpc |
| 51 | ERPC | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 52 | etox | 21.3 | 16.8 | 1 | 3 | blockchain_data; blockchain_rpc |
| 53 | FastNear | 21.3 | 16.8 | 3 | 3 | blockchain_data; blockchain_rpc |
| 54 | Fastnode.io | 21.3 | 16.8 | 4 | 3 | blockchain_data; blockchain_rpc |
| 55 | FlashBlock | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 56 | FluxRPC | 21.3 | 16.8 | 11 | 3 | blockchain_data; blockchain_rpc |
| 57 | GetBlock | 21.3 | 16.8 | 32 | 3 | blockchain_data; blockchain_rpc |
| 58 | Helius | 21.3 | 16.8 | 61 | 3 | blockchain_data; blockchain_rpc |
| 59 | Hydromancer | 21.3 | 16.8 | 2 | 3 | blockchain_data; blockchain_rpc |
| 60 | Hypedexer | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 61 | Imperator.co | 21.3 | 16.8 | 4 | 3 | blockchain_data; blockchain_rpc |
| 62 | Inodra | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 63 | Instanodes | 21.3 | 16.8 | 18 | 3 | blockchain_data; blockchain_rpc |
| 64 | Kaleido | 21.3 | 16.8 | 75 | 3 | blockchain_data; blockchain_rpc |
| 65 | Kriptonio | 21.3 | 16.8 | 1 | 3 | blockchain_data; blockchain_rpc |
| 66 | L0vd | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 67 | Launchnodes | 21.3 | 16.8 | 13 | 3 | blockchain_data; blockchain_rpc |
| 68 | LeoRPC | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 69 | Liquify | 21.3 | 16.8 | 14 | 3 | blockchain_data; blockchain_rpc |
| 70 | Luganodes | 21.3 | 16.8 | 16 | 3 | blockchain_data; blockchain_rpc |
| 71 | Node Forge | 21.3 | 16.8 | 3 | 3 | blockchain_data; blockchain_rpc |
| 72 | node101 | 21.3 | 16.8 | 11 | 3 | blockchain_data; blockchain_rpc |
| 73 | NodeFlare | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 74 | Nodefleet | 21.3 | 16.8 | 4 | 3 | blockchain_data; blockchain_rpc |
| 75 | Nodely | 21.3 | 16.8 | 3 | 3 | blockchain_data; blockchain_rpc |
| 76 | NodeReal | 21.3 | 16.8 | 20 | 3 | blockchain_data; blockchain_rpc |
| 77 | Nodies | 21.3 | 16.8 | 8 | 3 | blockchain_data; blockchain_rpc |
| 78 | Nodit | 21.3 | 16.8 | 66 | 3 | blockchain_data; blockchain_rpc |
| 79 | NoLimitNodes | 21.3 | 16.8 | 2 | 3 | blockchain_data; blockchain_rpc |
| 80 | Noode | 21.3 | 16.8 | 4 | 3 | blockchain_data; blockchain_rpc |
| 81 | NorthWest Nodes | 21.3 | 16.8 | 2 | 3 | blockchain_data; blockchain_rpc |
| 82 | Novacula | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 83 | NOWNodes | 21.3 | 16.8 | 10 | 3 | blockchain_data; blockchain_rpc |
| 84 | OBSRVR | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 85 | OnFinality | 21.3 | 16.8 | 6 | 3 | blockchain_data; blockchain_rpc |
| 86 | OrbitFlare | 21.3 | 16.8 | 2 | 3 | blockchain_data; blockchain_rpc |
| 87 | RadiumBlock | 21.3 | 16.8 | 1 | 3 | blockchain_data; blockchain_rpc |
| 88 | RockX | 21.3 | 16.8 | 19 | 3 | blockchain_data; blockchain_rpc |
| 89 | RouteMe.sh | 21.3 | 16.8 | 3 | 3 | blockchain_data; blockchain_rpc |
| 90 | RPC Fast | 21.3 | 16.8 | 24 | 3 | blockchain_data; blockchain_rpc |
| 91 | RpcNode | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 92 | Selvage Labs | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 93 | Shyft | 21.3 | 16.8 | 5 | 3 | blockchain_data; blockchain_rpc |
| 94 | SigmaCore | 21.3 | 16.8 | 3 | 3 | blockchain_data; blockchain_rpc |
| 95 | Sodae | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 96 | Solami | 21.3 | 16.8 | 1 | 3 | blockchain_data; blockchain_rpc |
| 97 | SolidRPC | 21.3 | 16.8 | 2 | 3 | blockchain_data; blockchain_rpc |
| 98 | SolSqueezer | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 99 | Spectrum | 21.3 | 16.8 | 4 | 3 | blockchain_data; blockchain_rpc |
| 100 | SpeedyNodes | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 101 | Stakely | 21.3 | 16.8 | 12 | 3 | blockchain_data; blockchain_rpc |
| 102 | Supanode | 21.3 | 16.8 | 12 | 3 | blockchain_data; blockchain_rpc |
| 103 | SwiftNodes | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 104 | Synapse | 21.3 | 16.8 | 3 | 3 | blockchain_data; blockchain_rpc |
| 105 | Tatum | 21.3 | 16.8 | 76 | 3 | blockchain_data; blockchain_rpc |
| 106 | Tenderly | 21.3 | 16.8 | 79 | 3 | blockchain_data; blockchain_rpc |
| 107 | TON API | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 108 | TONNode | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 109 | Triport | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 110 | TronGrid | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 111 | Validation Cloud | 21.3 | 16.8 | 25 | 3 | blockchain_data; blockchain_rpc |
| 112 | Venum | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 113 | Web3CDN | 21.3 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 114 | ZAN | 21.3 | 16.8 | 3 | 3 | blockchain_data; blockchain_rpc |
| 115 | Browserbase | 20.1 | 15.3 | — | 3 | browser_automation |
| 116 | Triton One | 19.2 | 16.8 | 21 | 3 | blockchain_data; blockchain_rpc |
| 117 | Allium | 18.3 | 12.8 | 78 | 3 | blockchain_data; blockchain_indexing |
| 118 | Bitquery | 18.3 | 12.8 | 21 | 3 | blockchain_data; blockchain_indexing |
| 119 | Blockchair | 18.3 | 12.8 | 9 | 3 | blockchain_data; blockchain_indexing |
| 120 | Chainbase | 18.3 | 12.8 | 10 | 3 | blockchain_data; blockchain_indexing |
| 121 | CODEX DATA | 18.3 | 12.8 | 12 | 3 | blockchain_data; blockchain_indexing |
| 122 | Envio | 18.3 | 12.8 | 13 | 3 | blockchain_data; blockchain_indexing |
| 123 | GoldRush | 18.3 | 12.8 | 38 | 3 | blockchain_data; blockchain_indexing |
| 124 | Hello Moon | 18.3 | 12.8 | 8 | 3 | blockchain_data; blockchain_indexing |
| 125 | Indexing Co | 18.3 | 12.8 | 7 | 3 | blockchain_data; blockchain_indexing |
| 126 | IndexSupply | 18.3 | 12.8 | 1 | 3 | blockchain_data; blockchain_indexing |
| 127 | Mobula | 18.3 | 12.8 | 10 | 3 | blockchain_data; blockchain_indexing |
| 128 | Moralis | 18.3 | 12.8 | 58 | 3 | blockchain_data; blockchain_indexing |
| 129 | Noves | 18.3 | 12.8 | 15 | 3 | blockchain_data; blockchain_indexing |
| 130 | Ormi Labs | 18.3 | 12.8 | 7 | 3 | blockchain_data; blockchain_indexing |
| 131 | PINAX | 18.3 | 12.8 | 18 | 3 | blockchain_data; blockchain_indexing |
| 132 | Sentio | 18.3 | 12.8 | 12 | 3 | blockchain_data; blockchain_indexing |
| 133 | Solana Tracker | 18.3 | 12.8 | — | 3 | blockchain_data; blockchain_indexing |
| 134 | SolanaStreaming | 18.3 | 12.8 | — | 3 | blockchain_data; blockchain_indexing |
| 135 | SonarX | 18.3 | 12.8 | 15 | 3 | blockchain_data; blockchain_indexing |
| 136 | SQD | 18.3 | 12.8 | 38 | 3 | blockchain_data; blockchain_indexing |
| 137 | Subscan | 18.3 | 12.8 | 1 | 3 | blockchain_data; blockchain_indexing |
| 138 | Tokenview | 18.3 | 12.8 | — | 3 | blockchain_data; blockchain_indexing |
| 139 | WatchData | 18.3 | 12.8 | 2 | 3 | blockchain_data; blockchain_indexing |
| 140 | Zerion | 18.3 | 12.8 | 72 | 3 | blockchain_data; blockchain_indexing |
| 141 | ZettaBlock | 18.3 | 12.8 | 7 | 3 | blockchain_data; blockchain_indexing |
| 142 | 01.ro | 18.1 | 16.8 | 10 | 3 | blockchain_data; blockchain_rpc |
| 143 | 0xFury | 18.1 | 16.8 | 2 | 3 | blockchain_data; blockchain_rpc |
| 144 | Blink | 18.1 | 16.8 | 7 | 3 | blockchain_data; blockchain_rpc |
| 145 | Block Stack | 18.1 | 16.8 | 32 | 3 | blockchain_data; blockchain_rpc |
| 146 | Bloq | 18.1 | 16.8 | 43 | 3 | blockchain_data; blockchain_rpc |
| 147 | ECAD Infra | 18.1 | 16.8 | 14 | 3 | blockchain_data; blockchain_rpc |
| 148 | Exaion | 18.1 | 16.8 | — | 3 | blockchain_data; blockchain_rpc |
| 149 | GlobalStake | 18.1 | 16.8 | 11 | 3 | blockchain_data; blockchain_rpc |
| 150 | InfStones | 18.1 | 16.8 | 34 | 3 | blockchain_data; blockchain_rpc |
| 151 | Nodeinfra | 18.1 | 16.8 | 2 | 3 | blockchain_data; blockchain_rpc |
| 152 | NodeOps | 18.1 | 16.8 | 26 | 3 | blockchain_data; blockchain_rpc |
| 153 | SenseiNode | 18.1 | 16.8 | 18 | 3 | blockchain_data; blockchain_rpc |
| 154 | Arcade | 16.0 | 8.4 | — | 3 | agent_tools; authorization |
| 155 | Composio | 14.7 | 6.9 | — | 3 | agent_tools |
| 156 | bloXroute Labs | 13.5 | 10.3 | 54 | 3 | blockchain_data |
| 157 | Dodo Payments | 13.2 | 7.5 | — | 3 | payments_processing |
| 158 | fal | 11.7 | 6.9 | — | 3 | model_inference |
| 159 | Venice | 11.7 | 6.9 | — | 3 | model_inference |
| 160 | Fern | 11.5 | 5.0 | — | 3 | dev_docs_sdk |
| 161 | Fractal ID | 10.8 | 10.3 | — | 3 | identity_verification |
| 162 | LangChain | 10.6 | 3.4 | — | 3 | agent_orchestration; observability |
| 163 | BlockRazor | 10.5 | 6.9 | 5 | 3 | blockchain_rpc |
| 164 | Solana Vibe Station | 10.5 | 6.9 | 3 | 3 | blockchain_rpc |
| 165 | CrewAI | 10.3 | 3.1 | — | 3 | agent_orchestration; workflow |
| 166 | Zenity | 10.1 | 8.4 | — | 3 | agent_tools; authorization |
| 167 | Fleek | 10.0 | 9.7 | — | 3 | cloud_compute; hosting |
| 168 | Cherry Servers | 9.6 | 6.2 | — | 3 | cloud_compute |
| 169 | RedSwitches | 9.6 | 6.2 | — | 3 | cloud_compute |
| 170 | velia.net | 9.6 | 6.2 | — | 3 | cloud_compute |
| 171 | Inngest | 9.6 | 3.1 | — | 3 | agent_orchestration; workflow |
| 172 | HoneyHive | 9.3 | 1.6 | — | 3 | observability |
| 173 | Mem0 | 9.2 | 1.2 | — | 3 | memory |
| 174 | E2B | 8.3 | 2.8 | — | 3 | code_sandbox |
| 175 | Mastra | 8.1 | 4.7 | — | 3 | agent_orchestration; observability; workflow |
| 176 | Etherspot | 7.9 | 3.4 | 7 | 3 | wallet_infra |
| 177 | Particle Network | 7.9 | 3.4 | 20 | 3 | wallet_infra |
| 178 | Shinami | 7.9 | 3.4 | 9 | 3 | wallet_infra |
| 179 | Hatchet | 7.9 | 1.2 | — | 3 | workflow |
| 180 | Fluence | 7.7 | 6.2 | — | 3 | cloud_compute |
| 181 | Spheron | 7.7 | 6.2 | — | 3 | cloud_compute |
| 182 | Swan Chain | 7.7 | 6.2 | — | 3 | cloud_compute |
| 183 | Mintlify | 7.7 | 5.0 | — | 3 | dev_docs_sdk |
| 184 | Conduit | 7.1 | 3.4 | 36 | 3 | hosting |
| 185 | Aleph Cloud | 7.0 | 6.2 | — | 3 | cloud_compute |
| 186 | Lyzr | 6.5 | 3.1 | — | 3 | agent_orchestration; workflow |
| 187 | AgentOps | 6.4 | 1.6 | — | 3 | observability |
| 188 | Pipedream | 5.8 | 1.2 | — | 3 | workflow |
| 189 | Biconomy | 5.4 | 3.4 | — | 3 | wallet_infra |
| 190 | Judgment Labs | 5.4 | 1.6 | — | 3 | observability |
| 191 | Openlayer | 5.4 | 1.6 | — | 3 | observability |
| 192 | PromptLayer | 5.4 | 1.6 | — | 3 | observability |
| 193 | Zep | 5.3 | 1.2 | — | 3 | memory |
| 194 | Dynamic | 4.7 | 3.4 | — | 3 | wallet_infra |
| 195 | Stackup | 4.7 | 3.4 | — | 3 | wallet_infra |
| 196 | ZeroDev | 4.7 | 3.4 | — | 3 | wallet_infra |
| 197 | Upstash | 4.7 | 2.8 | — | 3 | vector_db; workflow |
| 198 | Distributional | 4.7 | 0.0 | — | 3 | — |
| 199 | AgentMail | 4.5 | 1.2 | — | 3 | email_infra |
| 200 | AltLayer | 4.2 | 0.0 | 15 | 3 | — |
| 201 | Reddio | 4.2 | 0.0 | 2 | 3 | — |
| 202 | Cerbos | 3.2 | 1.6 | — | 3 | authorization |
| 203 | Blocknative | 2.0 | 0.0 | — | 3 | — |
| 204 | BlockSec | 1.5 | 0.0 | — | 3 | — |
| 205 | Astralane | 1.2 | 0.0 | 11 | 3 | — |
| 206 | Impossible Cloud | 1.0 | 0.0 | — | 3 | — |
| 207 | Pinata | 1.0 | 0.0 | — | 3 | — |

---

# 3. Removed list, 52 companies

| Company | Score | Staff | Reason code | Reason |
|---|---|---|---|---|

| Firecrawl | 68.3 | — | competitor | web data competitor, excluded by request |
| Apify | 64.7 | — | competitor | catalogue competitor and supplier, excluded by request |
| Cloudflare | 39.5 | — | large network | public company, edge network |
| Zapier | 32.4 | — | large SaaS | automation leader |
| Vercel | 31.7 | — | late-stage platform | large developer platform |
| Exa | 28.0 | — | competitor | web search competitor, excluded by request |
| Perplexity | 28.0 | — | AI major | consumer search brand |
| Alchemy | 24.3 | 373 | headcount 373 | large infrastructure vendor |
| ChainUp Cloud | 21.3 | 120 | headcount 120 | part of a large group |
| Infura | 21.3 | 14 | corporate product | product of ConsenSys |
| QuickNode | 21.3 | 110 | headcount 110 | large RPC vendor |
| Dune | 18.3 | 152 | headcount 152 | large analytics vendor |
| Etherscan | 18.3 | 41 | category leader | explorer leader |
| Kaiko | 18.3 | 224 | headcount 224 | market-data vendor |
| Nansen | 18.3 | 117 | headcount 117 | large analytics vendor |
| Blockdaemon | 18.1 | 210 | headcount 210 | large node vendor |
| Coinbase Cloud | 18.1 | 36 | exchange division | division of a listed exchange |
| IntellectEU | 18.1 | 222 | headcount 222 | large integrator |
| Modal | 16.7 | — | late-stage AI | compute platform |
| Anthropic | 15.5 | — | AI major | frontier model lab |
| DeepSeek | 15.5 | — | AI major | frontier model lab |
| Replicate | 15.5 | — | AI major | model hosting leader |
| Replit | 14.4 | — | late-stage SaaS | large dev platform |
| Stripe | 13.2 | — | large fintech | public-scale payments company |
| CoinGecko | 12.9 | — | category leader | market-data leader |
| OpenAI | 11.7 | — | AI major | frontier model lab |
| MoonPay | 10.7 | — | large fintech | fiat onramp leader |
| Transak | 10.7 | — | large fintech | fiat onramp vendor |
| Alibaba Cloud | 9.6 | — | hyperscaler | global cloud division |
| Amazon Web Services | 9.6 | — | hyperscaler | global cloud division |
| Google Cloud | 9.6 | — | hyperscaler | global cloud division, also a supplier |
| HUAWEI CLOUD | 9.6 | — | hyperscaler | global cloud division |
| IBM Cloud | 9.6 | — | hyperscaler | global cloud division |
| Oracle Cloud | 9.6 | — | hyperscaler | global cloud division |
| Hostinger | 8.6 | — | large host | global hosting group |
| Render | 8.6 | — | late-stage SaaS | hosting platform |
| Telnyx | 7.7 | — | large carrier | global carrier |
| 0x | 4.9 | — | large protocol | liquidity protocol company |
| Privy | 4.7 | — | acquired | acquired by Stripe |
| Safe | 4.7 | — | large foundation | wallet standard, foundation-run |
| Turnkey | 4.7 | — | late-stage | wallet infrastructure vendor |
| Ramp Network | 4.2 | — | large fintech | fiat onramp vendor |
| Deepgram | 3.8 | — | late-stage AI | voice AI leader |
| Resend | 3.8 | — | late-stage SaaS | email platform |
| MongoDB | 3.3 | — | public company | listed database vendor |
| Pinecone | 3.3 | — | late-stage SaaS | vector DB leader |
| LaunchDarkly | 2.5 | — | late-stage SaaS | feature-flag leader |
| Neon | 2.2 | — | late-stage SaaS | acquired-scale database vendor |
| Supabase | 2.2 | — | late-stage platform | large open-source platform |
| Storj | 1.0 | — | token-listed | listed storage network |
| Zeeve | 1.0 | 120 | headcount 120 | managed infra vendor |
| Certora | 0.8 | — | late-stage | security vendor |

---

# 4. Citations

## 4.1 Sources for the usebuy capability vector

| Source | URL | What it supports | Read |
|---|---|---|---|
| Gateway catalogue | https://gateway.usebuy.ai/v1/catalog | 170 capabilities, 10 providers, platform counts, prices, tokens, ERC-8004 registries, free SQD route | 2026-11-23 |
| Product docs | https://usebuy.ai/docs | x402 flow, EIP-3009 signing, MCP tools, Self proofs, VM pricing, sandbox | 2026-11-23 |
| Limits page | https://usebuy.ai/limits | per-route caps, body sizes, deadlines, fleet limits | 2026-11-23 |
| Product site | https://usebuy.ai | 782-tool claim, category price table, install commands | 2026-11-23 |
| npm registry | https://registry.npmjs.org/@celo%2Fbuy | 8 sub-packages, version count, maintainers | 2026-11-23 |
| GitHub | https://github.com/celo-org/buy-skill | repo ownership, MCP skill surface | 2026-11-23 |

## 4.2 Sources for the company data

| Source | File | Columns used |
|---|---|---|
| Infrastructure company list | `outputs/usebuy-infrastructure-2026-11-20/infrastructure-companies.csv` | `company`, `url`, `segment`, `infrastructure_category`, `service_summary`, `sales_route`, `commercial_evidence_type`, `directory_headcount`, `infra_services_sold` |

The CSV has 259 rows and 16 columns. Its own provenance is the `source_names` and `source_urls` columns. 176 rows come from the CompareNodes provider directory, 46 from the Chainstack directory, 27 from the DTCP report, and the rest from 9 other sources.

The CSV has two known weaknesses that carry into this model:

1. `directory_headcount` is filled for 132 of 259 rows, and all 132 are in the Web3 segment. It is self-reported by a directory and is unreliable at the low end. 11 rows show a headcount of 1.
2. `service_summary` is boilerplate for 125 rows. All 125 read "RPC node access and blockchain API infrastructure." This pushes those rows into an identical tag set and produces the 98-way tie at 21.3.

## 4.3 Sources for the removal rules

| Rule | Basis |
|---|---|
| Headcount of 150 or more | `directory_headcount` column. Only 132 rows have the value. |
| Hyperscaler, public company, category leader | Public knowledge. The CSV has no headcount for the AI segment, so size is judged by market position. |
| Firecrawl, Apify, Exa removed | Instruction from the user, 2026-11-23. |

## 4.4 Reproduce the result

```
cd outputs/usebuy-profile-2026-11-23
python3 scripts/rank_similarity.py --run examples/usebuy   # rebuilds similarity-ranking.csv
python3 filter_reachable.py    # rebuilds the reachable and removed files
```

Both scripts are deterministic. The same input gives the same ranking.

