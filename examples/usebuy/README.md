# Example run: useBuy.ai

One finished run of the pipeline, kept as a worked example. Every figure below
comes from the files in this folder.

| Field | Value |
|---|---|
| Subject | [useBuy.ai](https://usebuy.ai), an agent pay-per-request marketplace on Celo |
| Date | 2026-11-24 |
| Sourced | 259 companies |
| Kept | 207 reachable |
| Removed | 52, with a reason code each |
| Personal contacts | 36, held outside this repository |
| Capability tags | 31, seven of them core |

## What is here

| File | Holds |
|---|---|
| `run.json` | The run config: column map, model terms, tier cuts, reachability and enrichment rules |
| `company-profile.md` | What useBuy sells, in plain words |
| `service-catalogue-analysis.md` | Analysis of the 170 gateway routes |
| `icp.md` | The target profile: buyer, value, capability surface, anti-ICP |
| `taxonomy.csv` | 31 capability tags with weight, core flag and regex |
| `universe.csv` | 259 sourced companies, one row each |
| `scoring-model.md` | How the weights and tier cuts were set |
| `similarity-ranking.csv` | Every company, scored and tiered |
| `similarity-ranking-reachable.csv` | The 207 kept rows, contact columns removed |
| `similarity-ranking-removed.csv` | The 52 removed rows with `reason_code` and `reason` |
| `similarity-ranking.md` | The ranking as a readable table |
| `full-scoring-table.md` | Every scored row in one table |
| `reachable-shortlist.md` | The shortlist, tier by tier |
| `service-class-coverage.csv` | How many service classes each company sells |
| `multi-service-coverage.csv` | Which companies sell more than one product line |
| `service-inventory.csv` | The routes and services counted per company |

## How this run was scored

```
score = 0.88 * match_index + 0.07 * delivery + 0.05 * buyer
```

`match_index` is a weighted Jaccard score over the 31 tags, rescaled so the best
row reads 100.

| Tier | Rule | Companies |
|---|---|---|
| 1 direct | `match_index >= 55` and 2 or more core hits | 3 |
| 2 adjacent | `match_index >= 18` and 1 or more core hit | 13 |
| 3 different layer | everything else | 243 |

The removal rules:

| Rule | Effect |
|---|---|
| Headcount 150 or more | Remove |
| Known large brand or hyperscaler | Remove |
| Direct competitor | Remove |
| Marketplace supplier | Remove, and keep the link |

## Reproduce it

```bash
python3 scripts/rank_similarity.py --run examples/usebuy
python3 scripts/filter_reachable.py --run examples/usebuy
python3 scripts/service_class_coverage.py --run examples/usebuy
python3 frontend/build.py --run examples/usebuy
```

Stage 5 needs a Hunter key and spends credits, so this repository does not ship
its output. Add `HUNTER_API_KEY` to `~/.hermes/.env` and run:

```bash
python3 pipeline/run_pipeline.py --stage 5 --confirm-credits
```

## What the run taught

| Lesson | Detail |
|---|---|
| One source gives one bias | 176 of 259 rows came from a single directory, so the list held almost no multi-category companies |
| Summaries are boilerplate | 125 of 259 `service_summary` rows were marketing text. Tag from the service list |
| Ties are not a ranking | 101 companies tied at 21.3. Their order was noise |
| Breadth fights reachability | The companies that sell the most service classes are the ones you cannot email |
| Check the page limit | Hunter Free rejected `limit=50` with `pagination_error`. Use `limit=10` |
| Read back every write | One sheet write dropped a column and shifted every value left |

## Contact data

The 36 personal addresses are not in this repository. `outreach.csv`,
`similarity-ranking-contacts.csv` and `hunter-cache/` stay on the machine that
ran the enrichment, and the root `.gitignore` blocks them.
