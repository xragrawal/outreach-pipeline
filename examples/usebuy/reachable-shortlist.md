# Reachable shortlist: similarity ranking with large companies and three competitors removed

| Field | Value |
|---|---|
| Input | `similarity-ranking.csv` (259 companies) |
| Removed | 52 companies |
| Kept | 207 companies |
| Rule 1 | CSV headcount of 150 or more |
| Rule 2 | Hyperscaler, public company, category leader, or a division of one |
| Rule 3 | Excluded by request: Firecrawl, Apify, Exa |
| Output | `similarity-ranking-reachable.csv`, `similarity-ranking-removed.csv` |
| Script | `filter_reachable.py` |
| Date | 2026-11-23 |

---

## 1. What was removed

52 companies. 49 were removed on size, and 3 on request.

| Group | Count | Companies |
|---|---|---|
| Hyperscalers | 6 | AWS, Google Cloud, Alibaba Cloud, HUAWEI CLOUD, IBM Cloud, Oracle Cloud |
| Late-stage SaaS and platforms | 11 | Supabase, Vercel, Zapier, Pinecone, Neon, Resend, Render, Replit, LaunchDarkly, Modal, Deepgram |
| AI majors | 5 | OpenAI, Anthropic, Perplexity, Replicate, DeepSeek |
| Crypto majors and exchange divisions | 13 | Coinbase Cloud, Alchemy, QuickNode, Blockdaemon, Infura, Dune, Nansen, Kaiko, Etherscan, CoinGecko, 0x, Safe, Storj |
| Fintech majors | 4 | Stripe, MoonPay, Transak, Ramp Network |
| Hosting, carrier, and network | 3 | Hostinger, Telnyx, Cloudflare |
| Other large vendors | 7 | MongoDB, Privy, Turnkey, Certora, ChainUp Cloud, Zeeve, IntellectEU |
| **Excluded by request** | **3** | **Firecrawl, Apify, Exa** |

The full list with a reason code per company is in `similarity-ranking-removed.csv`. Every row is reversible: delete it from the `REMOVE` dict in `filter_reachable.py` and rerun.

Two removals need a note:

- **Google Cloud** is both a hyperscaler and a current supplier. It sells usebuy the VM route.
- **Apify** is now removed. It was a direct structural comparable and also a supplier of 27 catalogue routes. Removing it drops the last supplier-competitor overlap from the list.

## 2. The reachable ranking

| # | Company | Score | Capability index | Headcount | Matched capabilities |
|---|---|---|---|---|---|
| 1 | **BlockRun** | 95.1 | 100 | — | api gateway, pay-per-call, web search, blockchain data, model inference |
| 2 | Uniblock | 48.5 | 48 | 16 | api gateway, blockchain data, RPC |
| 3 | blockmachine | 46.8 | 46 | 1 | pay-per-call, blockchain data, RPC |
| 4 | Merge | 35.4 | 31 | — | api gateway |
| 5 | Crossmint | 30.2 | 32 | — | agent payments, wallet |
| 6 | Speakeasy | 28.1 | 27 | — | MCP server, developer docs and SDK |
| 7 | Parallel | 28.0 | 24 | — | web search |
| 8 | Tavily | 28.0 | 24 | — | web search |
| 9 | LI.FI | 27.8 | 31 | — | api gateway |
| 10 | Chaingateway.io | 24.3 | 20 | 2 | blockchain data, RPC, wallet |
| 11 | thirdweb | 24.3 | 20 | 19 | blockchain data, RPC, wallet |
| 12 | Browser Use | 23.9 | 15 | — | browser automation |
| 13 | Amforc | 23.7 | 23 | 5 | blockchain data, RPC, compute |
| 14 | Blink Labs | 23.7 | 20 | 6 | blockchain data, RPC, indexing |
| 15 | Goldsky | 23.7 | 20 | 30 | blockchain data, RPC, indexing |
| 16 | StreamingFast | 23.7 | 20 | — | blockchain data, RPC, indexing |
| 17 | 1RPC | 21.3 | 17 | 7 | blockchain data, RPC |
| 18 | 4EVERLAND | 21.3 | 17 | 5 | blockchain data, RPC |
| 19 | All That Node | 21.3 | 17 | 59 | blockchain data, RPC |
| 20 | Allnodes | 21.3 | 17 | 6 | blockchain data, RPC |
| 21 | Ankr | 21.3 | 17 | 87 | blockchain data, RPC |
| 22 | ARKHIA | 21.3 | 17 | 3 | blockchain data, RPC |
| 23 | Asternodes | 21.3 | 17 | — | blockchain data, RPC |
| 24 | AvaCloud | 21.3 | 17 | — | blockchain data, RPC |
| 25 | AZXA.IO | 21.3 | 17 | 4 | blockchain data, RPC |

Rank 17 onward is the RPC tie block. 98 companies share the score 21.3. Their order carries no meaning.

## 3. Who to contact first

**Group A: the single comparable (1).** BlockRun. It is now the only company in the list that shares more than one core capability with usebuy. It runs an agent-facing gateway with pay-per-call billing. Treat it as a competitor to watch, and a possible supply partner.

**Group B: one-capability adjacents (8).** Uniblock, blockmachine, Merge, Crossmint, Speakeasy, Parallel, Tavily, LI.FI. Each shares one strong capability. A conversation is worth it only if you want that capability in the catalogue.

Ranked by likely value to usebuy:

| Company | Why it is worth a call |
|---|---|
| Crossmint | Agent payments is usebuy's second pillar. It is the only company in the list that sells it. |
| Uniblock | Same aggregation model across blockchain providers. A supply candidate for the RPC route. |
| Tavily, Parallel | Web search and research APIs. This is the largest gap in the catalogue. |
| Merge | Unified API aggregation. A structural comparable, not a supply candidate. |
| blockmachine | Metered RPC resale. Small, but the same billing model. |
| Speakeasy | Generates MCP servers. A distribution partner, not a data vendor. |
| LI.FI | Cross-chain aggregation. Low fit. |

**Group C: the RPC tail (about 98).** Allnodes, Ankr, 1RPC, Helius, GetBlock, Dwellir, dRPC and the rest. They match on blockchain data and RPC only. usebuy buys one RPC route today. Contact one or two as price checks, not all of them.

## 4. Size profile of the kept set

| Band | Count |
|---|---|
| Small, under 50 staff | 108 |
| Mid, 50 to 149 staff | 12 |
| Unknown, no headcount in the CSV | 87 |

The 87 unknown rows are mostly the AI segment. The CSV has no headcount for that segment at all. "Unknown" is not a size claim, so check each one before you write.

The 12 mid-size companies:

| Company | Staff | Score |
|---|---|---|
| All That Node | 59 | 21.3 |
| Ankr | 87 | 21.3 |
| Chainstack | 55 | 21.3 |
| Helius | 61 | 21.3 |
| Kaleido | 75 | 21.3 |
| Nodit | 66 | 21.3 |
| Tatum | 76 | 21.3 |
| Tenderly | 79 | 21.3 |
| Allium | 78 | 18.3 |
| Moralis | 58 | 18.3 |
| Zerion | 72 | 18.3 |
| bloXroute Labs | 54 | 13.5 |

All 12 are reachable. None is large enough to ignore on size.

## 5. Kept but not a prospect

| Company | Note |
|---|---|
| Chainstack | Already supplies the Celo RPC route |
| SQD | Already supplies the free multi-chain data route |

## 6. What the three removals cost you

Firecrawl, Apify, and Exa were three of the four strongest matches. Removing them changes what the list can tell you.

- **The list no longer contains a scraping comparable.** BlockRun is a gateway, not a scraper. There is now no company in the list that sells web scraping at scale.
- **The list no longer contains a catalogue comparable.** Apify was the only marketplace of third-party actors.
- **Web search is still covered**, by Parallel and Tavily.

If the goal is to size up the competitive set, keep them in a separate competitor file. If the goal is an outreach list, the removal is correct, because you do not cold-email your own category.

## 7. Files

| File | Contents |
|---|---|
| `similarity-ranking-reachable.csv` | 207 companies, re-ranked, with size band and supplier flag |
| `similarity-ranking-removed.csv` | 52 removed companies with a reason code |
| `filter_reachable.py` | The filter. Edit `REMOVE` or `HEADCOUNT_LIMIT` and rerun. |
| `similarity-ranking.csv` | The unfiltered 259 |
