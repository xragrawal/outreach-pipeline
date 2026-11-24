# Pipeline page

One page that shows the five-stage run: the ranking, the contacts and the
multi-line companies. Every figure on the page is read from a file at build time.

With the small server in `serve.py`, the page can also run each stage and show
the gate output as it happens.

## Run the stages

```bash
python3 frontend/serve.py
python3 frontend/serve.py --run runs/acme
python3 frontend/serve.py --port 9000 --no-open
```

The server prints `http://127.0.0.1:8787/` and opens it. It builds the page from
the run folder first, so a new run shows up without a separate build. The page
then shows a **Run** button on each stage and **Run stages 1–4** in the section
head.

| Route | Does |
|---|---|
| `GET /api/state` | Lists the stages, whether their outputs exist, and which spend credits |
| `POST /api/setup` | Creates a run from the company and ICP form, then makes it active |
| `POST /api/candidates` | Validates and writes the Stage 2 candidate CSV |
| `POST /api/run` | Starts one stage. Body: `{"stage": 4, "confirm_credits": false}` |
| `GET /api/job?id=…` | Returns the state, exit code and output of a job |

The server binds to `127.0.0.1` only. It runs `pipeline/run_pipeline.py` with a
fixed argument list, so it cannot run any other command. It runs one job at a
time. Stage 5 needs `confirm_credits`, and the page asks first.

## Create a run from the page

The setup form writes a new folder under `runs/`. It records the company brief
in `run.json` and `icp.md`. It also creates `taxonomy.csv` from the weighted
capability lines. Use `Capability | weight` on each line.

The source panel accepts the Stage 2 CSV. It requires the configured company,
category, summary and services columns. After import, the existing stage runner
uses the same gate and worker code as the command-line flow.

Opened from `file://` or by a static host, the page finds no API. It hides the
Run buttons and shows the command to start the server.

## Build

```bash
python3 frontend/build.py --run examples/usebuy
```

`build.py` reads these files from the run folder and writes `index.html`:

| File | Feeds |
|---|---|
| `run.json` | subject, date, sheet link, model terms |
| `universe.csv` | companies sourced, source types |
| `similarity-ranking.csv` | the ranking, the tie count |
| `similarity-ranking-reachable.csv` | the kept count and the contact cells |
| `similarity-ranking-removed.csv` | the removed count, when it exists |
| `service-class-coverage.csv` | the service-class table, when it exists |
| `multi-service-coverage.csv` | the multi-line table, when it exists |
| `outreach.csv` | the contact column, when it exists |
| `similarity-ranking-removed.csv` | removed count |
| `taxonomy.csv` | tag count, weight sum |
| `outreach.csv` | the contact table. Optional: without it the page hides the contacts and says so |
| `multi-service-coverage.csv` | the multi-line cards |

With no `--run`, the build uses the run named in `pipeline/pipeline.json`.

The build fails if any `__PLACEHOLDER__` is left unreplaced.

## Files

- `template.html` — the page with `/*__DATA__*/{}` and `__*__` placeholders.
- `build.py` — the builder.
- `serve.py` — the local server and stage runner.
- `index.html` — the output. Open it in a browser. No server is needed.
- `assets/fonts/GeistPixel.ttf` — the real Geist Pixel file, ELSH axis.
- `assets/logo/` — the lockups, marks and favicon from the brand kit.

## Brand rules applied

Read from https://antseed-home.vercel.app/brand/ (`DESIGN.md`, `AGENTS.md`).

- White rail on a dotted page: a 2px dot every 8px, rail 1312px at most, rail pad
  `clamp(20px, 9.64vw, 145px)`.
- Each section draws its own dotted top line. The rail draws the left, right and
  bottom lines.
- Geist Pixel for the H1, titles, eyebrows, figures and step numbers; ELSH 11 for
  the H1, 40 for titles, 20 for the rest. Geist and Geist Mono for text.
- The H1 is two tones (`#1c1c1c` then `#595959`) at 0.82 opacity. Section titles
  take a full stop.
- The page is flat. No shadow on the page or on cards. Depth is glass over a
  painting, and this page has no painting.
- One filled green button per block. Everything else is a ghost button.
- Day and night are two themes, not a filter. The logo inverts at night.

## No contact data

This public copy has no personal addresses. `outreach.csv`,
`similarity-ranking-contacts.csv` and `hunter-cache/` stay out of the repository.
The ranking file here has its contact columns removed.

## Limits

- Geist and Geist Mono load from Google Fonts. Without a network the page falls
  back to the system sans.
- The tables scroll sideways on a phone. Below 760px the ranking drops the core
  and contact columns, and the contacts become one card per person.
- Chrome headless cannot render below 500px wide. To check the phone layout,
  put `index.html` in a 390px iframe.
- Without contact data the page prints `withheld` in the email metric. It never
  claims zero.
- The page does not reload itself after a stage. It offers a Reload button, so a
  running stage never swaps the figures under you.
