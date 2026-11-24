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

## Start a new run

Do not copy `examples/usebuy`. That folder carries one subject's tags, cuts and
rules. Make an empty run instead:

```bash
python3 scripts/new_run.py --slug acme --subject "Acme.ai"
```

That writes `runs/acme/` with a `run.json` of defaults, an `icp.md` of TODO
lines, an empty `taxonomy.csv` and a `universe.csv` with only a header. `runs/`
is git-ignored, so a working run never reaches the repo.

Then fill four files, in this order:

| File | What you write |
|---|---|
| `runs/acme/icp.md` | Buyer, value proposition, capability surface, weights, core capabilities, anti-ICP, evidence |
| `runs/acme/taxonomy.csv` | One tag per row: `tag,weight,core,regex`. Optional `guard` column for a second regex that must also match |
| `runs/acme/universe.csv` | The sourced companies, one row each |
| `runs/acme/run.json` | Subject, column map, tier cuts, reachability rules, handoff |

Check the first three stages before you spend anything:

```bash
python3 pipeline/run_pipeline.py --run runs/acme --stage 1,2,3
```

Stage 1 fails while `icp.md` still holds a TODO line. Fix it, run again.

Then score, enrich and write the handoff:

```bash
python3 pipeline/run_pipeline.py --run runs/acme --stage 4
python3 pipeline/run_pipeline.py --run runs/acme --stage 5 --confirm-credits
python3 frontend/build.py --run runs/acme
```

Stage 4 writes the ranking and the reachability filter. Stage 5 calls Hunter,
keeps only personal addresses, and writes `outreach.csv` in priority order.
Stage 5 spends credits, so it needs `--confirm-credits`.

The column names in `universe.csv` are your choice. Point `columns` in
`run.json` at them. The default map is `company`, `url`, `segment`, `category`,
`summary`, `services`, `sales_route`, `evidence_type`, `headcount`.

`pipeline/PIPELINE.md` gives the stage contracts and the lessons from the
example run.

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
| `scripts/build_outreach.py` | Turns contacts into `outreach.csv`, in priority order. |
| `scripts/new_run.py` | Makes an empty run folder from the template. |
| `pipeline/run.template.json` | The defaults a new run starts from. |
| `frontend/build.py` | Renders a run into one static HTML page. |
| `frontend/serve.py` | Serves the page and runs stages on request. |
| `examples/usebuy/` | One finished run, end to end. |

## Run the stages from the page

```bash
python3 frontend/serve.py
```

The server prints a link and opens it. Every stage then has a **Run** button.
Press one and the log streams under the stages: each gate line appears as it
passes. **Run stages 1–4** walks the chain in order.

The page can also create a working run. Enter the company, buyer, value
proposition, weighted capabilities, core capabilities, anti-ICP and evidence.
The server writes the run folder and makes it active for the current session.
Import the candidate CSV in Stage 2, then run the waterfall from Stage 1.

The server binds to `127.0.0.1` only, and it runs one fixed command list, so it
cannot run anything else. It runs one stage at a time. Stage 5 asks for a
confirmation first, because it spends Hunter credits.

The figures on the page come from the files at build time. After a stage, press
**Reload the page** to read them again.

Without the server the page is plain HTML. Opened from `file://` or served by a
static host, it hides the Run buttons and shows the command to start the server.

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
