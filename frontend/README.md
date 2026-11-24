# Pipeline page

One static page that shows the five-stage run: the ranking, the contacts and the
multi-line companies. Every figure on the page is read from a file at build time.

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
| `similarity-ranking-removed.csv` | removed count |
| `taxonomy.csv` | tag count, weight sum |
| `outreach.csv` | the contact table. Optional: without it the page hides the contacts and says so |
| `multi-service-coverage.csv` | the multi-line cards |

With no `--run`, the build uses the run named in `pipeline/pipeline.json`.

The build fails if any `__PLACEHOLDER__` is left unreplaced.

## Files

- `template.html` — the page with `/*__DATA__*/{}` and `__*__` placeholders.
- `build.py` — the builder.
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
