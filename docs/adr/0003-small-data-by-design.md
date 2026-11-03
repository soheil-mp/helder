# ADR-0003: Small data by design, with enforced budgets

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Storage is limited and some sources are large: the unfiltered RWS latest-observation layer is
more than 325 MB as CSV, the catalogue 6.6 MB, and historic archives far larger. The platform
must still show real data in real time.

## Decision

- **Select, don't mirror.** A *watchlist* (configuration) names the series Helder follows: by
  default the live water quality series near drinking water intakes, bathing waters and key
  lakes, plus their upstream stations. Laboratory and groundwater history is bounded by area,
  parameters and years.
- **Filter at the source.** CQL filters, bounding boxes, `propertyName` and narrow periods, so
  only needed rows cross the network.
- **Budgets as code.** Per-source download budgets per day and a total storage budget
  (`HELDER_STORAGE_BUDGET_MIB`, default 2 GiB). A budget guard fails closed: a connector stops
  before exceeding its budget and raises an alert.
- **Tiered retention.** Raw 10-minute observations are kept 90 days; hourly and daily aggregates
  and all exceedances are kept indefinitely; snapshots are expired and compacted on schedule.
- **No data in Git.** Only small recorded fixtures under `tests/fixtures/`.

## Consequences

- The full platform runs on a laptop and in CI with a few hundred megabytes of data.
- Coverage is a deliberate selection, documented in the watchlist and on the dashboard.
- Budget metrics become first-class observability signals.
