# useBuy outreach pipeline

A five-stage pipeline that turns one target company into a ranked, contactable
list. Built for [useBuy.ai](https://usebuy.ai), an agent pay-per-request
marketplace on Celo.

The run starts with a target profile, sources candidate companies, scores each
one on shared capabilities, removes the ones that are too large to reach, and
ends with a named contact and a reason to write.

## Stages

| # | Stage | Question | Output |
|---|---|---|---|
| 1 | ICP generation | Who do we want, what do they sell, what do we value? | `icp.md`, `pipeline/taxonomy.csv` |
| 2 | Sourcing | Which companies could match, and where do we find them? | `universe.csv` |
| 3 | Scoring model | Which parameters separate a good match from a bad one? | `pipeline/scoring-model.md` |
| 4 | Scoring | How close is each company, and is it reachable? | `similarity-ranking.csv`, `similarity-ranking-reachable.csv`, `similarity-ranking-removed.csv` |
| 5 | Enrichment and outreach | Who do we contact, at which address, and why now? | `outreach.csv`, `similarity-ranking-contacts.csv` |

Each stage ends with a gate. A failed gate stops the run.

## The score

```
score = 0.88 * match_index + 0.07 * delivery + 0.05 * buyer
```

`match_index` is a weighted Jaccard score over 31 capability tags, rescaled so
the best row reads 100. Seven tags are core. Capability overlap carries most of
the weight on purpose.

Tiers:

- Tier 1: `match_index >= 55` and at least 2 core tags.
- Tier 2: `match_index >= 18` and at least 1 core tag.
- Tier 3: everything else.

## Run it

```bash
python3 pipeline/run_pipeline.py --stage 1,2
python3 pipeline/run_pipeline.py --stage all --dry-run
python3 pipeline/run_pipeline.py --stage 5 --confirm-credits
```

Stage 5 spends paid API credits, so it needs `--confirm-credits`. The default is
a dry run.

## Files

| File | What it holds |
|---|---|
| `pipeline/PIPELINE.md` | The playbook: stage contracts, gates, lessons. |
| `pipeline/pipeline.json` | Machine-readable stage config and tuned constants. |
| `pipeline/run_pipeline.py` | The orchestrator and the five gates. |
| `pipeline/taxonomy.csv` | 31 capability tags with weight, core flag and regex. |
| `pipeline/scoring-model.md` | How the weights were set and why. |
| `icp.md` | The target profile from stage 1. |
| `universe.csv` | 259 companies, one row each. |
| `rank_similarity.py` | Builds the ranking. |
| `filter_reachable.py` | Removes companies that are too large to reach. |
| `enrich_hunter.py` | Finds personal addresses through Hunter. |
| `service_class_coverage.py` | Groups the market into 16 service classes. |
| `frontend/` | A static page that shows the run. |
| `company-profile.md` | What useBuy sells, in plain words. |
| `service-catalogue-analysis.md` | Analysis of the 170 gateway capabilities. |
| `multi-service-coverage.md` | Which companies sell more than one product line. |
| `full-scoring-table.md` | Every scored row, in one table. |

## No contact data in this repository

The full run holds 36 personal email addresses. They are not here. `outreach.csv`,
`similarity-ranking-contacts.csv` and `hunter-cache/` stay on the machine that
ran the enrichment, and `.gitignore` blocks them.

`similarity-ranking-reachable.csv` in this repository is the 207-row ranking with
the contact columns removed.

## The page

```bash
python3 frontend/build.py
open frontend/index.html
```

The build reads the CSVs and writes `frontend/index.html`. No server is needed.
Without `outreach.csv` the page drops the contact column and says so.

The page follows the Antseed brand kit: white rails on a dotted page, Geist
Pixel for headings and figures, flat surfaces, day and night themes.

## Data

The company list comes from a public infrastructure survey. Headcount comes from
public directories. The Hunter Free plan allows 50 credits, so enrichment runs in
small batches and caches each answer in `hunter-cache/`.

## Licence

The code is free to reuse. The company data comes from public sources. Check the
terms of each source before you republish it.
