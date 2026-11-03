# ADR-0011: dbt-core for SQL transformations

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Most transformations (deduplication, version selection, daily means, joins to registries,
dimensional marts) are naturally SQL. They need tests, contracts, documentation and lineage.

## Decision

Use **dbt-core 1.12** with **dbt-duckdb** on the DuckLake catalog:

- Layers `staging` → `intermediate` → `marts`, matching the `clean` and `curated` schemas.
- Incremental `microbatch` models for observation tables, keyed on phenomenon time.
- Model contracts on every mart, unit tests for every non-trivial model, generic and singular
  data tests, and exposures for API endpoints and exports.
- SQLFluff (DuckDB dialect with dbt templater) in pre-commit and CI.
- Only dbt-core (Apache-2.0); the dbt Fusion engine (ELv2) is not used.

## Consequences

- The industry-standard workflow that reviewers recognise.
- Python-only logic (QC, physics, travel time) stays in Python packages, called from Dagster.

## Alternatives considered

- **SQLMesh:** virtual environments and column-level lineage are attractive, but the Dagster
  integration is community-maintained.
