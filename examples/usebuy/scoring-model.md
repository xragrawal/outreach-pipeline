# Scoring model

| Field | Value |
|---|---|
| Stage | 3 of 5 |
| Subject | useBuy.ai |
| Inputs | `taxonomy.csv`, `icp.md` |
| Used by | `scripts/rank_similarity.py` |
| Date | 2026-11-24 |

---

## 1. Terms

| Term | Weight | Range | Signal |
|---|---|---|---|
| Capability | 0.88 | 0 to 100 | Weighted Jaccard over the 31-tag taxonomy, rescaled to the best row |
| Delivery | 0.07 | 0 to 100 | API, metered billing, self-serve signup, free tier |
| Buyer | 0.05 | 0 to 100 | Sells to agents, developers, or data teams |

```
score = 0.88 * match_index + 0.07 * delivery + 0.05 * buyer
```

Sum: 1.00.

## 2. Capability match

For a company vector `c` and the subject vector `u`, both sparse over the 31 tags:

```
capability_match = sum(w[t] for t in c & u) / sum(w[t] for t in c | u)
```

`w[t]` is the subject weight of tag `t`, not a flat 1. So covering `social_media_data` is worth more than covering `observability`.

Rescale:

```
match_index = capability_match / max(capability_match over all rows) * 100
```

The best row always scores 100. This makes the number readable, and it makes the score relative to the universe, not absolute.

## 3. Delivery signals

| Signal | Points | Test |
|---|---|---|
| Sells an API or endpoint | 40 | category or services mention API, endpoint, gateway |
| Metered or per-request pricing | 30 | usage, per request, credits, pay as you go |
| Self-serve signup | 20 | sign up, free tier, try free, dashboard |
| Published pricing | 10 | pricing page or price table |

## 4. Buyer signals

| Buyer | Points |
|---|---|
| Agents and AI developers | 100 |
| Developers and data teams | 70 |
| Web3 developers | 60 |
| Enterprise platform teams | 30 |
| Consumers | 0 |

## 5. Tiers

| Tier | Rule | Meaning |
|---|---|---|
| 1 | `match_index >= 55` and `core_hits >= 2` | Same business |
| 2 | `match_index >= 18` and `core_hits >= 1` | Adjacent layer |
| 3 | everything else | Different layer |

Core tags: `social_media_data`, `web_scraping`, `api_gateway`, `pay_per_call`, `agent_payments`, `web_search`, `mcp_server`.

## 6. Known limits

| Limit | Effect | Mitigation |
|---|---|---|
| Text-only tagging | A company that sells a capability without naming it is missed | Add a manual review pass on the top 20 |
| Relative rescale | Scores are not comparable across runs | Compare `capability_match`, not `match_index` |
| Large tie blocks | 101 rows can share one score | Report the tie; never present the order as a ranking |
| Boilerplate summaries | 125 of 259 rows repeat the same text | Tag from the service list, not the summary |
| No revenue or intent | Cannot rank by deal value or timing | Add paid data sources |

## 7. Worked example

| Company | Capability | Match index | Delivery | Buyer | Score |
|---|---|---|---|---|---|
| BlockRun | 0.321 | 100.0 | 85 | 70 | 95.1 |
| Uniblock | 0.153 | 47.7 | 60 | 60 | 48.5 |

BlockRun covers gateway, pay-per-call, search, blockchain data, and model inference. Uniblock covers gateway and blockchain data only. The gap comes from the weighted overlap, not from the tie-breakers.
