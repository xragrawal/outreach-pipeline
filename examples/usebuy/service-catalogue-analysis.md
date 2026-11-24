# usebuy.ai: analysis of the services it provides

| Field | Value |
|---|---|
| Subject | buy (usebuy.ai), agent service marketplace on Celo |
| Data source | Live gateway catalogue `https://gateway.usebuy.ai/v1/catalog`, read 2026-11-23 |
| Also read | Product site, docs, limits page, Agent402 tool index |
| Catalogue size | 170 capabilities |
| Available now | 149 (87.6%) |
| Unavailable now | 21 (12.4%) |
| Free route | SQD Portal, 7 endpoints |
| Inventory export | `service-inventory.csv` (170 rows, same folder) |

All counts below come from the live catalogue. The storefront count is different and is discussed in section 7.

---

## 1. What the service actually is

buy sells **read access to public data, plus a small amount of compute**. It is a payment gateway in front of other vendors' APIs.

The agent does not get an account with TikHub, Apify, or Google. It gets one wallet, one 402 handshake, and a proxied call. buy handles the upstream relationship, the billing, and the settlement.

This matters for the analysis. buy owns almost none of the supply. It owns the payment rail, the identity layer, and the storefront.

## 2. Inventory at a glance

| Dimension | Value |
|---|---|
| Total capabilities | 170 |
| Curated, productised IDs | 11 |
| Raw upstream passthroughs | 159 |
| Distinct upstream providers | 10 |
| Platforms covered | 10 |
| Capabilities with a published price | 25 (14.7%) |
| Published price points | 73 |
| Price range | $0.0036 to $12.003 |
| Median published price | $0.025 |

The catalogue splits into two very different halves:

- **11 curated services.** Clean names, documented parameters, stable contracts. Example: `instagram.profile`, `x.posts.search`, `flights.search`, `browser.sessions.create`.
- **159 passthrough services.** The ID is the upstream vendor's own route name. Example: `monid.instagram.tikhub.api-v1-instagram-v2-fetch-user-info`.

That 11-to-159 ratio is the single most important fact about the service line. Only 6% of the catalogue is a product. The rest is a proxy.

## 3. Service families

| Family | Count | Share |
|---|---|---|
| Posts and content | 38 | 22% |
| Search | 35 | 21% |
| Comments | 25 | 15% |
| Profile and account lookup | 23 | 14% |
| Other (IDs, trends, subreddit metadata, ads) | 24 | 14% |
| Followers and audience | 9 | 5% |
| Analytics and metrics | 7 | 4% |
| Enrichment (email, person) | 5 | 3% |
| Transcripts and captions | 4 | 2% |

Read that as a product statement. **buy sells social listening primitives.** It does not sell actions. There is no post, reply, follow, message, or upload endpoint in the gateway.

An agent can watch a market with buy. It cannot act on that market with buy.

## 4. Platform coverage

| Platform | Profile | Posts | Search | Comments | Followers | Analytics | Transcripts | Enrichment | Other | Total |
|---|---|---|---|---|---|---|---|---|---|---|
| Instagram | 8 | 10 | 9 | 3 | 2 | 1 | – | – | 2 | 35 |
| TikTok | 2 | 6 | 5 | 4 | 3 | 6 | – | – | 6 | 32 |
| YouTube | 1 | 8 | 8 | 6 | – | 4 | 1 | – | 4 | 32 |
| LinkedIn | 8 | 2 | 7 | 3 | – | – | – | 4 | 1 | 25 |
| Reddit | 1 | 8 | 2 | 7 | – | – | – | – | 4 | 22 |
| X | 3 | 4 | 3 | 2 | 4 | – | – | – | 3 | 19 |
| Flights | – | – | 1 | – | – | – | – | – | 1 | 2 |
| Browser | – | – | – | – | – | – | – | – | 1 | 1 |
| Chainstack RPC | – | – | – | – | – | – | – | – | 1 | 1 |
| Cencori inference | – | – | – | – | – | – | – | – | 1 | 1 |

Four observations:

1. **Depth is uneven.** TikTok has 6 analytics endpoints and 2 profile endpoints. Instagram has 8 profile endpoints and 1 analytics endpoint. The shape is inherited from each upstream vendor, not designed.
2. **LinkedIn is a people-data product.** 8 profile endpoints and 4 enrichment endpoints. It is the only platform that returns emails.
3. **YouTube is the only platform with transcripts** in the catalogue, and only 1 endpoint does it. Captions are a high-value agent primitive, and coverage is thin.
4. **X is under-served.** 19 endpoints for the platform that agent builders care about most. 4 of them are follower lists.

### The count overstates breadth

170 routes carry 165 distinct titles. The difference is small, but the duplication is visible:

- Instagram has 4 title pairs that appear twice each: comment replies, location posts, user posts, and user reels. That is 8 entries for 4 functions.
- Instagram has three generations of one lookup: `Fetch User Info`, `Fetch User Info By Username`, and `Fetch User Info By Username V3`. TikTok, YouTube, and LinkedIn show the same `v1` and `v2` pattern.
- 5 Apify Instagram actors repeat functions that TikHub already serves.

So 170 is a route count, not a capability count. A buyer should pick one route per function, not treat the number as breadth.

## 5. Supply concentration

| Upstream provider | Capabilities | Share | Unavailable |
|---|---|---|---|
| TikHub | 121 | 71.2% | 2 |
| Apify | 27 | 15.9% | 15 |
| MrScraper | 7 | 4.1% | 0 |
| Ploid | 6 | 3.5% | 1 |
| Strale | 2 | 1.2% | 2 |
| ContactOut | 2 | 1.2% | 0 |
| Clay | 1 | 0.6% | 0 |
| Kadec0 | 1 | 0.6% | 1 |
| First-party browser worker | 1 | 0.6% | 0 |
| No provider listed | 2 | 1.2% | 0 |

**TikHub is a single point of failure for 71% of the catalogue.** One contract change, one rate-limit change, or one legal notice removes most of the product.

The Apify tier is the opposite problem. 15 of 27 Apify capabilities are down, which is a 56% failure rate. The Apify tier looks abandoned or unmaintained.

Unavailable by platform: Instagram 6, LinkedIn 7, YouTube 3, X 2, TikTok 1, Reddit 1, Flights 1.

## 6. Pricing

### Only 15% of the catalogue has a public price

| Item | Value |
|---|---|
| Capabilities with `priceOptions` | 25 of 170 |
| Price points published | 73 |
| Cheapest | $0.0036 |
| Median | $0.025 |
| Most expensive | $12.003 |

145 capabilities publish no price. For those, the catalogue gives no number at all. The docs say the 402 quote is authoritative, which is true, but it means a buyer cannot budget from the storefront.

### Price by platform (published points only)

| Platform | Points | Min | Median | Max |
|---|---|---|---|---|
| TikTok | 9 | $0.0036 | $0.0060 | $0.0230 |
| X | 4 | $0.0038 | $0.0090 | $0.0630 |
| Instagram | 7 | $0.0060 | $0.0190 | $0.0350 |
| YouTube | 12 | $0.0048 | $0.0780 | $12.0030 |
| LinkedIn | 27 | $0.0070 | $0.1030 | $0.6030 |
| Reddit | 9 | $0.0070 | $0.1050 | $0.1510 |
| Browser | 5 | $0.0036 | $0.0048 | $0.0091 |

The ordering is sensible. LinkedIn and Reddit cost the most because they are the hardest to scrape and the most valuable for sales data. TikTok and X are commodity-cheap.

### Price by function

| Function | Points | Median |
|---|---|---|
| Enrichment (email, person) | 6 | $0.7030 |
| Transcripts | 3 | $0.0530 |
| Comments | 18 | $0.0330 |
| Search | 28 | $0.0321 |
| Profile lookup | 9 | $0.0190 |
| Analytics | 3 | $0.0130 |
| Browser sessions | 5 | $0.0048 |

Enrichment is 30 to 40 times the median price. That is the margin centre of the catalogue. A work email is worth more than a thousand scraped posts.

### Outliers

| Service | Price |
|---|---|
| YouTube channel business dataset (Apify) | $1.2030 to $12.0030 |
| LinkedIn profile search (Apify) | $0.3330 to $0.6030 |
| YouTube video scraper (Apify) | $0.0312 to $0.2742 |
| LinkedIn profile search by name (Ploid) | $0.0230 to $0.2030 |

The $12.003 YouTube entry is 480 times the median. It is a bulk dataset product sold as a single call. It is also the only item that looks like a data-licensing deal rather than a scrape.

### Fixed routes

| Route | Price |
|---|---|
| Chainstack Celo RPC | $0.01 per request, up to 2000 JSON-RPC calls per batch |
| Cencori chat completion | $0.01 per completion, one model only |
| Google Cloud VM, `e2-micro` to `e2-standard-8` | $0.0168 to $0.5361 per hour |
| SQD Portal multi-chain data | Free |

The Chainstack route is the best value in the catalogue on a unit basis. One cent buys a batch of 2000 RPC calls.

## 7. What the storefront claims versus what the gateway sells

| Claim | Reality |
|---|---|
| "782 tools in the catalogue" (dated 2026-10-13) | Gateway has 170. Agent402 now lists 638. 170 + 638 = 808. |
| "Compute, blockchain, data and browser access" | Compute is 1 VM route and 1 closed-beta model. Blockchain is 1 chain (Celo) and 1 free data route. Browser is 1 route. Data is 159 of 170. |
| Categories on the homepage such as "Payments & x402", "Sanctions screening", "Agent memory & coordination", "Routing & delegation", "Skill packs" | None of these exist in the gateway catalogue. They are Agent402 tools listed on the same page. |

The storefront merges two catalogues. buy's own gateway sells social data and a little compute. Agent402 supplies the payments, identity, and utility tools.

A buyer who reads the homepage and then calls `/v1/catalog` will not find most of what the homepage listed. That is a trust problem, not a counting problem.

## 8. Free tier and partner routes

**SQD Portal, free.** 7 endpoints across 100+ chains: dataset list, chain head, finalized head, dataset metadata, timestamp-to-block lookup, block stream, finalized stream. Limited to 120 requests per minute per IP with a burst of 20.

This is the strongest asset in the catalogue. Multi-chain data with no payment and no account is exactly what an agent needs to bootstrap. It is also the only service that gives buy a reason to be opened before a wallet exists.

**Partner routes.** Chainstack Celo RPC and Cencori inference are resold at a flat $0.01. Both are single-purpose and both are mainnet-only. They exist to prove the rail works outside social data.

## 9. Service gaps

What an agent platform needs, and whether buy has it:

| Need | Status |
|---|---|
| Social data | Strong. 159 endpoints. |
| Multi-chain blockchain data | Free but narrow. One free provider, one paid chain. |
| General web search and crawl | Not in the gateway. Only via Agent402. |
| LLM inference | One model, closed beta. |
| Code execution sandbox | No. Google VMs only, no sandbox API. |
| Email and voice | No. |
| Memory and vector storage | No. |
| Workflow and queues | No. |
| Payments to other agents | No first-party tool. Agent402 covers it. |
| Write actions on social platforms | No. Read-only. |

The pattern is clear. buy is a data marketplace with a payments rail attached. It is not yet a general agent infrastructure layer.

## 10. Commercial read

1. **The moat is the rail, not the catalogue.** Anyone can resell TikHub. The 402 settlement, the keychain wallet, the Self proof, and the ERC-8004 registry are the hard parts.
2. **Concentration risk is severe.** 71% of the catalogue depends on one vendor.
3. **The pricing signal is weak.** 85% of services have no public price. That limits self-serve conversion and makes comparison shopping impossible.
4. **The best product is buried.** 11 clean services sit behind 159 vendor-named routes. The storefront should lead with the 11.
5. **Free SQD is the acquisition channel.** It is the only entry point that needs no wallet and no payment.
6. **The 21 dead capabilities cost trust.** A 12% failure rate on a storefront reads as neglect.

## 11. Recommendations

If you are buying from them:

1. Start with the 11 curated IDs. Ignore the `monid.*` routes until you need one specific endpoint.
2. Use `buy quote` before every first call. 145 services have no listed price.
3. Prefer TikHub-backed routes over Apify-backed routes. Apify is 56% down.
4. Use the SQD free route for chain data. Do not pay for it.
5. Set `--max-amount` on every call. Payments are final and there are no refunds.

If you are assessing them as a company:

1. Ask for the take rate and the TikHub contract terms.
2. Ask why 15 Apify capabilities are down.
3. Ask whether the 782 figure will be corrected.
4. Ask for the roadmap on write actions, sandboxes, and memory. Those are the three gaps that decide whether the product stays a data shop.

## 12. Method note

Counts come from the live `/v1/catalog` JSON, read on 2026-11-23. Function labels are my classification, built from the capability ID, title, and description. Price statistics use only the 73 published price points. Median figures are per price point, not per call.

The full inventory is in `service-inventory.csv` with these columns: id, title, platform, provider, function, available, price_min_usd, price_max_usd, price_points, method, url, pricing_model.
