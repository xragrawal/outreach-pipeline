# Multi-service comparables: companies that span many categories like usebuy

| Field | Value |
|---|---|
| Question | Which companies cover many service categories at once, the way usebuy does? |
| Input | 259-row CSV, plus primary research outside it |
| Finding | One of 259 spans more than three categories. Ten outside companies do. |
| Files | `multi-service-comparables.csv`, this report |
| Date | 2026-11-23 |

---

## 1. The gap in the CSV

I checked the 259 rows for breadth: how many of usebuy's 8 core categories each company covers.

| Categories covered | Companies |
|---|---|
| 0 | 74 |
| 1 | 180 |
| 2 | 3 |
| 3 | 1 |
| 4 or more | 1 |

The best is BlockRun, at 5 of 8: gateway, payments, search, crypto data, and inference. It is still not a data marketplace. It holds no social inventory and no scraping inventory.

Only 4 of the 259 cover three or more. The other 255 sell one layer.

The reason is structural. The CSV was built from blockchain directories and AI reports. It captures vendors that sell one layer to one buyer. It does not capture multi-category marketplaces.

## 2. The eight categories

These are the surfaces usebuy actually sells, from its live catalogue.

1. Social media data
2. Web scraping and crawling
3. Web search and research
4. Browser and automation
5. Crypto and blockchain data
6. Model inference and generation
7. Agent payments and metering
8. MCP and agent gateway

A true multi-service comparable covers 5 or more.

## 3. The shortlist

| # | Company | Categories | Scale | Rail | Evidence |
|---|---|---|---|---|---|
| 1 | **Monid** | 7 | 3,179 endpoints, 102 providers | Prepaid plus x402 | Vendor page |
| 2 | **PayAPI Market** | 5 | 3,558 listed, 2,337 verified | USDC on 4 chains | Vendor page |
| 3 | **Vaaya** | 4 | not published | Pay per call | Listing page |
| 4 | **Bounty API** | 3 | about 10 routes | x402 on Base | Vendor page |
| 5 | **x402 Bazaar** | 3 | 112 APIs, 11 categories | USDC | Search snippet |
| 6 | **APIMesa** | 3 | not published | Credits | Search snippet |
| 7 | **AgentCash** | 2 | not published | x402 | Search snippet |
| 8 | **AIsa** | 2 | not published | Pay per result | Search snippet |
| 9 | hiapi | 1 | not published | Pay as you go | Directory |
| 10 | AIMLAPI | 1 | 1,000+ models | Pay as you go | Directory |

Rank 9 and 10 are model gateways. They cover one usebuy category. I list them to show where the boundary is, not as comparables.

## 4. Finding 1: Monid is probably usebuy's supplier

This is the most important result of the search.

**The evidence:** every one of usebuy's 159 passthrough routes starts with the prefix `monid.`

```
monid.instagram.tikhub.api-v1-instagram-v2-general-search
monid.linkedin.apify.harvestapi-linkedin-profile-search
monid.x.tikhub.api-v1-twitter-web-fetch-search-communities
```

**Monid's own numbers:** 3,122 to 3,179 enabled endpoints, from 102 providers, as of 14 November 2026. It covers social media, scraping, lead generation, search and SEO, ecommerce, finance, travel, news, crypto, and generative AI.

**What this means:** usebuy's 170 routes are a narrow slice of Monid's 3,179. usebuy resells one supplier family (TikHub 121, Apify 27, MrScraper 7) through a Monid-shaped catalogue, then adds its own payment rail and Celo settlement.

So usebuy is not a marketplace in the same sense. It is a reseller with a storefront and a payments layer. Monid is the marketplace.

**Caution:** I infer this from the route prefix, not from a published statement. usebuy does not name Monid in its docs.

## 5. Finding 2: the real competitive set is small and new

The full set of pay-per-call agent marketplaces with multi-category breadth is about five companies, not fifty.

| Company | Endpoints | Categories |
|---|---|---|
| Monid | 3,179 | 12 |
| PayAPI Market | 35,970 | 6 |
| x402 Bazaar | 112 | 11 |
| Bounty API | ~10 | 6 |
| APIMesa | not stated | 3 |

That is the whole set I could find. The CSV's 259 rows contain none of them.

## 6. Finding 3: two different businesses share the word "marketplace"

| Model | Who | How it earns | Buyer |
|---|---|---|---|
| Curated reseller | Monid, usebuy, Bounty API | Markup or flat fee per call | An agent with a funded wallet |
| Open directory | PayAPI Market, x402 Bazaar | 0% commission, listing fees or none | Any agent that finds the listing |

PayAPI Market takes 0% of each job. Monid marks up. usebuy sits closer to Monid: it resells and bills per request.

If usebuy wants to keep its margin, the open directory model is a threat, not a peer.

## 7. Where usebuy still differs

| Trait | usebuy | Best comparable |
|---|---|---|
| Social data depth | 165 of 170 routes | Monid, similar depth |
| Settlement chain | Celo only, 42220 | PayAPI, 4 chains |
| Identity and reputation | ERC-8004 plus Self.xyz | Nobody in this set |
| Token set | USDC, USDT, USAT | USDC mostly |
| Free tier | SQD route, 120 rpm | Not offered |
| Catalogue size | 170 | Monid 3,179 |

Two things are genuinely unusual: the ERC-8004 identity and reputation layer, and the free SQD data route. Both are small, but neither appears in any comparable.

## 8. What I could not verify

| Item | Status |
|---|---|
| Monid supply relationship | Inference from route naming, not a published claim |
| APIMesa catalogue size | Site blocks plain fetches |
| x402 Bazaar endpoint count | From a search snippet, not the live index |
| AgentCash and AIsa scale | Not published |
| Revenue or funding for any of the ten | Not researched |

## 9. Recommendation

1. **Watch Monid first.** It is the closest thing to usebuy's upstream and it is bigger by 19 times. If it adds Celo settlement, usebuy loses its main difference.
2. **Do not treat PayAPI Market as a supplier.** Its zero-commission model undercuts resale. Track it as a pricing threat.
3. **Use Bounty API as the proof of shape.** Ten routes, five categories, pay per call. It shows a small team can look like usebuy. That means the barrier is low.
4. **Keep the ERC-8004 layer.** It is the one thing in the set nobody else has.

## 10. Sources

| Source | URL | Read |
|---|---|---|
| Monid product page | https://monid.ai/info/api-marketplace-that-lets-ai-agents-pay-per-call | 2026-11-23 |
| PayAPI Market catalogue | https://payapi.market/marketplace | 2026-11-23 |
| Bounty API homepage | https://bountyapi.com | 2026-11-23 |
| x402 Bazaar | https://www.x402bazaar.org | 2026-11-23, snippet |
| APIMesa | https://apimesa.com | 2026-11-23, snippet |
| AgentCash | https://agentcash.dev | 2026-11-23, snippet |
| AIsa | https://aisa.one | 2026-11-23, snippet |
| AI Catalog, Monid alternatives | https://aicatalog.app/tools/monid/alternatives/ | 2026-11-23 |
| usebuy live catalogue | https://gateway.usebuy.ai/v1/catalog | 2026-11-23 |
