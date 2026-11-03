# ADR-0010: Dagster for orchestration

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Batch connectors, backfills, revision capture, dbt models, assessments, exports, compaction and
budget checks depend on each other and run at different cadences. Data quality checks should
live next to the data they guard.

## Decision

Use **Dagster 1.13** with software-defined assets:

- Assets per source and layer, daily partitions for time-based data and static partitions per
  source for registries.
- `dagster-dbt` loads every dbt model as an asset with its tests as asset checks.
- Sensors react to Kafka offsets and to budget events; schedules drive daily jobs.
- Asset checks block downstream assets on failed contracts (`blocking=True`).
- Freshness policies express the SLOs (for example: curated sensor marts no older than
  30 minutes).
- Concurrency pools limit simultaneous requests per source.

## Consequences

- One UI for lineage, runs, checks and freshness.
- The real-time path (Quix Streams) stays outside Dagster; Dagster orchestrates everything
  that is batch.

## Alternatives considered

- **Airflow 3:** task-centric; asset-awareness is newer and less integrated with dbt.
- **Kestra 2:** strong event-driven YAML flows, but weaker typing and Python asset model.
- **Prefect 3:** flexible, but no first-class asset checks or dbt asset integration of the same
  depth.
