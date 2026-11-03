# ADR-0009: Bitemporal observations that keep every revision

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

RWS first publishes values as `Ongecontroleerd` and may later replace them with
`Gecontroleerd` values, corrections or deletions. Helder's own QC flags change when rules change.
Alerts must remain explainable after the data they were based on has been revised.

## Decision

Every observation row carries two time axes:

- **Valid time:** `phenomenon_time` (when the water was measured, UTC).
- **Recorded time:** `recorded_from` and `recorded_to` (when Helder believed this version).

A new version of an observation closes the previous version's `recorded_to` instead of
overwriting it. The natural key is `(series_id, phenomenon_time)`; each version has a content
hash so identical re-deliveries are dropped. QC flags are stored per observation version and per
rule-set version. "As of" views give the state at any past moment; "current" views give the
newest version.

## Consequences

- Alerts, exceedances and reports record the snapshot and rule-set versions they used.
- Revision statistics (how often and how much RWS corrects values) become a product.
- Storage grows with revisions; retention and compaction keep it within budget.
