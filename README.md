# ICP to outreach pipeline

A five-stage pipeline that turns one target company into a ranked, contactable
list of companies that look like it.

You describe the target. The pipeline sources candidate companies, scores each
one on shared capabilities, removes the ones too large to reach, and ends with a
named contact and a reason to write.

Nothing about the target is hard-coded. A run is a folder. The engine is
separate.

```
pipeline/     the engine: orchestrator, stage config, playbook
scripts/      the four worker scripts
frontend/     a static page that renders a run
examples/     one finished run, kept as a worked example
```

## Stages

| # | Stage | Question | Output |
|---|---|---|---|
| 1 | ICP generation | Who do we want, what do they sell, what do we value? | `icp.md`, `taxonomy.csv` |
| 2 | Sourcing | Which companies could match, and where do we find them? | `universe.csv` |
| 3 | Scoring model | Which parameters separate a good match from a bad one? | `scoring-model.md` |
| 4 | Scoring | How close is each company, and is it reachable? | `similarity-ranking*.csv` |
| 5 | Enrichment and outreach | Who do we contact, at which address, and why now? | `outreach.csv` |

Each stage ends with a gate. A failed gate stops the run.

## The score

```
score = 0.88 * match_index + 0.07 * delivery + 0.05 * buyer
```

`match_index` is a weighted Jaccard score over the capability tags in
`taxonomy.csv`, rescaled so the best row reads 100. Capability overlap carries
most of the weight on purpose: the question is "do they sell what we sell".

Tiers stop a high score from hiding a false positive:

- Tier 1: high match index, at least 2 core capabilities.
- Tier 2: medium match index, at least 1 core capability.
- Tier 3: everything else.

The exact cuts are per run. They live in `run.json`.

## A run is a folder

Every number that names the subject lives in the run folder, not in the code.

| File | Holds |
|---|---|
| `run.json` | Subject, column map, model terms, tier cuts, reachability rules, enrichment rules, handoff |
| `taxonomy.csv` | Capability tags with weight, core flag and regex |
| `icp.md` | The target profile from stage 1 |
| `universe.csv` | The sourced companies, one row each |
| `scoring-model.md` | How the weights were set and why |

The worker scripts take `--run <folder>` and read everything from there. With no
`--run`, they use the folder named in `pipeline/pipeline.json`.

## Run it

```bash
python3 pipeline/run_pipeline.py --stage 1,2
python3 pipeline/run_pipeline.py --stage all --dry-run
python3 pipeline/run_pipeline.py --stage 5 --confirm-credits
python3 pipeline/run_pipeline.py --run examples/usebuy --stage 4
```

Stage 5 spends paid API credits, so it needs `--confirm-credits`. The default is
a dry run.

To start a new run, copy `examples/usebuy` to a new folder, replace the
artefacts, and edit `run.json`. `pipeline/PIPELINE.md` gives the stage contracts
and the lessons from the example run.

## Files

| File | What it holds |
|---|---|
| `pipeline/PIPELINE.md` | The playbook: stage contracts, gates, lessons. |
| `pipeline/pipeline.json` | The stage list and the default run. |
| `pipeline/run_pipeline.py` | The orchestrator and the five gates. |
| `scripts/rank_similarity.py` | Builds the ranking from `taxonomy.csv` and `run.json`. |
| `scripts/filter_reachable.py` | Removes companies that are too large to reach. |
| `scripts/enrich_hunter.py` | Finds personal addresses through Hunter. |
| `scripts/service_class_coverage.py` | Groups the market into service classes. |
| `frontend/build.py` | Renders a run into one static HTML page. |
| `examples/usebuy/` | One finished run, end to end. |

## The page

```bash
python3 frontend/build.py --run examples/usebuy
open frontend/index.html
```

The build reads the CSVs and writes `frontend/index.html`. No server is needed.
When the run has no `outreach.csv`, the page drops the contact column and says
so. The checked-in page is the output of the example run.

The page follows the Antseed brand kit: white rails on a dotted page, Geist
Pixel for headings and figures, flat surfaces, day and night themes.

## No contact data in this repository

Personal email addresses are not here. `outreach.csv`,
`similarity-ranking-contacts.csv`, `hunter-cache/` and `hunter-account.json`
stay on the machine that ran the enrichment, and `.gitignore` blocks them.

The ranking in `examples/usebuy/` is the kept rows with the contact columns
removed. Rebuild it with the scripts to add your own.

## Data

The example company list comes from public infrastructure directories.
Headcount comes from public sources. The Hunter Free plan allows 50 credits, so
enrichment runs in small batches and caches each answer in `hunter-cache/`.

## Licence

The code is free to reuse. The company data comes from public sources. Check the
terms of each source before you republish it.
