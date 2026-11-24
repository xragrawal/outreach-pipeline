# ICP to outreach: a five-stage pipeline

| Field | Value |
|---|---|
| Purpose | Turn one target company into a ranked, contactable list of similar companies |
| Proven on | useBuy.ai, 259 companies, 36 personal contacts |
| Entry point | `pipeline/run_pipeline.py` |
| Config | `pipeline/pipeline.json` |
| Date | 2026-11-24 |

---

## The five stages

| # | Stage | Question it answers | Main output |
|---|---|---|---|
| 1 | ICP generation | Who do we want, and what do we value? | `icp.md`, `pipeline/taxonomy.csv` |
| 2 | Sourcing | Which companies could match, and where do we find them? | `universe.csv` |
| 3 | Scoring model | Which parameters separate a good match, and how much does each count? | `pipeline/scoring-model.md` |
| 4 | Scoring | How close is each company, and is it reachable? | `similarity-ranking*.csv` |
| 5 | Enrichment and handoff | Who do we contact, at which address, and why now? | `similarity-ranking-contacts.csv`, `outreach.csv` |

Each stage has a gate. A gate is a cheap check that the output can be used. A failed gate stops the run.

```bash
python3 pipeline/run_pipeline.py --dry-run       # show the plan
python3 pipeline/run_pipeline.py --stage 1,2     # run two stages
python3 pipeline/run_pipeline.py --stage all     # run everything
```

Stage 5 spends API credits. It does nothing unless you add `--confirm-credits`.

---

## Stage 1: ICP generation

**Question:** Who do we want, and what do we value?

The ICP is not a paragraph. It is a machine-readable model with four parts.

| Part | What it holds | Why it matters |
|---|---|---|
| Buyer | Who pays, what they need, how they pay, what they refuse | Sets the buyer term and the anti-ICP |
| Value proposition | The three or four things the subject actually does | Stops you copying the marketing page |
| Capability surface | A flat list of capabilities, each with a weight | Becomes the scoring vector |
| Anti-ICP | Who is excluded, and why | Removes the large and the irrelevant |

**Method:** read the product, not the pitch. Open the live catalogue or API index. Count what is actually sold. Weight each capability by how much of the product it is.

For useBuy, social data is 165 of 170 routes, so it carries 0.95. Model inference is one route, so it carries 0.20.

**Output:** `icp.md` plus `pipeline/taxonomy.csv`.

**Gate:** every tag has a positive weight, a regex, and at least one core tag exists. The ICP file has all required sections.

**Failure mode:** weights copied from a competitor's site. They will not match your product, and the ranking will follow the wrong shape.

**Lesson from the run:** the first weight table was wrong because it counted words, not routes. Count the inventory.

---

## Stage 2: Sourcing

**Question:** Which companies could match, and where do we find them?

**Method:** build the universe from at least three source types. One source gives you one bias.

| Source type | What it gives | Bias |
|---|---|---|
| Directory | Long tail, one category per vendor | Misses companies that span categories |
| Review site | Buyer language, pricing signals | Skews to paid tiers |
| Market report | Named leaders, funding | Small sample |
| Marketplace catalogue | Live inventory and prices | Only listed vendors |
| Competitor customer list | Proven demand | Hard to obtain |
| Funding database | Size and stage | No product detail |

**Output:** `universe.csv`. One row per company, with an id column and at least three text fields.

**Gate:** rows above zero, no duplicate ids, every text field present.

**Failure mode:** one source only. In the useBuy run, 176 of 259 rows came from one directory. That is why the CSV held almost no multi-category companies.

**Lesson from the run:** 125 of 259 `service_summary` rows were boilerplate. Tag from the specific service list, not the summary.

---

## Stage 3: Scoring model

**Question:** Which parameters separate a good match, and how much does each count?

**Method:** choose a small number of terms, then defend each weight with evidence.

| Term | Weight | Signal | Why this weight |
|---|---|---|---|
| Capability | 0.88 | Weighted Jaccard over the taxonomy | The question is "do they sell what we sell" |
| Delivery | 0.07 | API, metered, self-serve | Same product, wrong sales motion is a weak match |
| Buyer | 0.05 | Sells to agents and developers | Same product, wrong buyer is a weak match |

Capability must dominate. A tie-breaker that can move the rank is not a tie-breaker.

**Tiers** stop a high score from hiding a false positive.

| Tier | Rule |
|---|---|
| 1 | match index 55 or more, and 2 or more core hits |
| 2 | match index 18 or more, and 1 or more core hit |
| 3 | everything else |

**Output:** `pipeline/scoring-model.md`, plus the weights already in `taxonomy.csv`.

**Gate:** the three terms sum to 1.0, all tags carry a weight, tiers are ordered.

**Failure mode:** equal weights. Then a company that sells one core capability scores the same as a company that sells five.

**Lesson from the run:** rescaled scores make the output readable, but they hide the raw distance. Keep `capability_match` next to `match_index`.

---

## Stage 4: Scoring

**Question:** How close is each company, and is it reachable?

**Method:**

1. Tag every company with the regex rules.
2. Compute the weighted Jaccard score against the subject vector.
3. Rescale so the best company scores 100.
4. Add the delivery and buyer terms.
5. Sort, assign tiers, then remove the unreachable.

**Reachability rules:**

| Rule | Action |
|---|---|
| Headcount 150 or more | Remove |
| Known large brand | Remove, with a reason code |
| Direct competitor | Remove |
| Every removal | Keeps a `reason_code` and a one-line note |

**Output:** `similarity-ranking.csv`, `similarity-ranking-reachable.csv`, `similarity-ranking-removed.csv`.

**Gate:** the ranking is sorted, kept plus removed equals total, no kept row reaches the size limit, and any large tie block is reported.

**Failure mode:** treating a tie as a ranking. In the useBuy run, 101 companies tied at 21.3. Their order was noise.

**Lesson from the run:** breadth and reachability pull in opposite directions. The companies that sell the most service classes are the ones you cannot email. Report that tension; do not hide it with a filter.

---

## Stage 5: Enrichment and outreach handoff

**Question:** Who do we contact, at which address, and why now?

**Method:** one domain search per company. Keep only a personal address. Rank the candidate by title, then by confidence.

| Rule | Value |
|---|---|
| Provider | Hunter `domain-search` |
| Page limit | 10 |
| Cost | 1 credit per domain |
| Address type | `personal` only |
| Rejected local parts | `info`, `hello`, `sales`, `partnerships`, and 50 more |
| Title priority | Founder, CEO, CTO, head of, VP, director, manager |
| Status values | `found`, `generic_only`, `not_found`, `not_run`, `error` |

**Output:** `similarity-ranking-contacts.csv` with seven contact columns, then `outreach.csv` with the handoff fields.

| Handoff field | Rule |
|---|---|
| `priority` | Tier 1 now, tier 2 this week, tier 3 batch |
| `reason_to_contact` | One line, drawn from the matched capabilities |
| `contact_email` | Blank unless `found` and personal |

**Gate:** every `found` row has a name and an email, no generic address leaked, all status values are known.

**Failure mode:** spending the credit budget on domains with no published addresses. Two of 16 searches returned nothing.

**Lesson from the run:** the free plan rejected `limit=50` with `pagination_error`. Use `limit=10`. Cache every raw response so a re-run costs nothing.

---

## Artifact contracts

| Artifact | Key columns | Producer |
|---|---|---|
| `icp.md` | Seven sections | Stage 1 |
| `taxonomy.csv` | `tag`, `weight`, `core`, `regex` | Stage 1 |
| `universe.csv` | id, three text fields | Stage 2 |
| `scoring-model.md` | terms, weights, tiers | Stage 3 |
| `similarity-ranking.csv` | `score`, `match_index`, `matched_capabilities`, `tier` | Stage 4 |
| `similarity-ranking-reachable.csv` | ranking plus `headcount` | Stage 4 |
| `similarity-ranking-removed.csv` | ranking plus `reason_code`, `reason` | Stage 4 |
| `similarity-ranking-contacts.csv` | seven contact columns | Stage 5 |
| `outreach.csv` | contact, `priority`, `reason_to_contact` | Stage 5 |

## Gates

| Gate | Checks |
|---|---|
| `icp` | Required sections present; every tag weighted and rule-backed; core set not empty |
| `source` | Rows above zero; no duplicate ids; text fields present |
| `model` | Terms sum to 1.0; every tag weighted; tiers ordered |
| `score` | Sorted; kept plus removed equals total; no oversized kept row; tie block reported |
| `enrich` | Every `found` row complete; no generic address; known status values |

## Publishing

The last step is a write to Google Sheets, then a read-back.

| Rule | Why |
|---|---|
| Write every column, every row | A single missing column shifts the whole sheet |
| Verify every cell against the CSV | A silent shift is worse than a failed write |
| Keep a second tab for the analysis view | The shortlist and the ranking answer different questions |
| Freeze the header | It survives sorting |

**Lesson from the run:** one write dropped a column and moved every value left by one. The check caught it. Always read back.

## Running it for a new ICP

1. Copy `pipeline/` to the new project folder.
2. Edit `pipeline.json`: set `subject`, `workdir`, `source_csv`, and the text fields.
3. Write `icp.md` and `pipeline/taxonomy.csv` for the new subject.
4. Run `--stage 1,2` and fix any gate failure.
5. Run `--stage 3,4` and read the tie report before you trust the order.
6. Set `min_score` from the tier-1 cut, then run stage 5 with `--confirm-credits`.

## What is not generic yet

| Item | State |
|---|---|
| `rank_similarity.py` | Holds the useBuy weights inline. Read them from `taxonomy.csv` to reuse. |
| `filter_reachable.py` | Holds the removal list inline. Move it into `pipeline.json`. |
| `enrich_hunter.py` | Holds the rules inline. The config already mirrors them. |
| Sheet layout | Fixed to the useBuy columns. Map it per project. |

The orchestrator and the gates are generic. The three worker scripts are not. Moving their constants into `pipeline.json` is the next refactor.
