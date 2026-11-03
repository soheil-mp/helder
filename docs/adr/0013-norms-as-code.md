# ADR-0013: Norms as code, with legal provenance and validity dates

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Helder judges values against many yardsticks: Bkl environmental quality standards (annual
average and maximum concentrations), drinking water limits, the chloride intake agreements,
Bathing Water Directive classes, cyanobacteria protocol levels and voluntary targets. They differ
in legal force, scope (water type, compartment, use), aggregation rule and validity period, and
they change over time (for example PFAS limits from 12 January 2026).

## Decision

- Norms live in `reference/norms/*.yaml`, validated by a JSON Schema. Each entry has: ID,
  observed property (Aquo), value and unit, **aggregation rule** (instantaneous, daily mean,
  annual mean, P90 or P95 of log10 values, maximum), scope (compartment, water category, use
  such as "drinking water intake"), **legal force** (`law`, `agreement`, `guideline`,
  `voluntary`), **source citation** (document, article, table, page, URL), `valid_from` and
  `valid_to`, and the date it was transcribed and by whom it was reviewed.
- An evaluation engine applies the right aggregation, the half-LOQ rule (2009/90/EC), and
  reports exceedance, headroom and data sufficiency (for example "not enough samples for a
  BWD classification").
- Every norm has at least one worked-example test taken from its source or computed by hand.
- The UI and API always show legal force and source next to any judgement.

## Consequences

- Judgements are reproducible for any date, with the norms valid on that date.
- Adding a norm is a reviewed data change, not a code change.
- Values marked "to transcribe" in the research cannot be used until transcribed and tested.
