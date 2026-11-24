# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary users are operators who build B2B lead lists from one target company.

This user needs one local workspace for the company brief, ICP, sourcing, scoring, filtering, and outreach handoff.

## Product Purpose

The product turns one company profile into a ranked and contactable list of similar companies.

Success means the user can create a run, pass each gate, and inspect each narrowing step from the browser.

## Positioning

The product keeps the ICP, scoring rules, reachability limits, evidence, and outputs inside one auditable run folder.

## Operating Context

The user starts the local server and works through a five-stage pipeline.

The browser calls only fixed local endpoints.

Stage 5 can spend Hunter credits and always needs confirmation.

## Capabilities and Constraints

- Create a run for one target company.
- Define the buyer, value proposition, weighted capabilities, core capabilities, anti-ICP, and evidence.
- Import candidate companies as CSV data.
- Run the five existing stages in order.
- Stop when a gate fails.
- Keep working runs and personal contact data outside Git.
- Preserve the existing pipeline contracts and scoring model.
- Assumption: one operator uses one active run per local server session.
- Assumption: sourcing remains an imported company list because no sourcing provider exists in this repository.

## Brand Commitments

Preserve the Antseed name, supplied logo assets, Geist Pixel headings, dotted rails, day and night themes, and direct product language.

## Evidence on Hand

- The five stage contracts live in `pipeline/pipeline.json`.
- The gate logic lives in `pipeline/run_pipeline.py`.
- The worked example lives in `examples/usebuy/`.
- The brand assets live in `frontend/assets/`.
- No customer claims, benchmarks, or testimonials are available.

## Product Principles

- Show the narrowing logic at every stage.
- Keep every state and failure visible.
- Require evidence before paid enrichment.
- Keep generated data traceable to a run folder.
- Make local operation safe by limiting server actions.

## Accessibility & Inclusion

Support keyboard input, clear focus states, reduced motion, and responsive use on desktop and mobile web.
