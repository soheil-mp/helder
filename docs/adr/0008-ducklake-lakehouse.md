# ADR-0008: DuckLake on PostgreSQL and S3-compatible storage

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Helder needs analytical storage with snapshots (to audit what was known when an alert fired),
schema evolution, cheap appends every few minutes, and fast SQL for dbt, the API and exports.
The data fits comfortably in a few gigabytes.

## Decision

- **DuckLake 1.0** is the table format: metadata in **PostgreSQL 18**, data as Parquet in an
  S3-compatible bucket served by **RustFS 1.0** (SeaweedFS as the documented fallback).
- **DuckDB 2.0** is the engine for dbt, Dagster assets, the API and exports.
- Stream micro-batches use DuckLake **data inlining**, so small commits land in the catalog and
  are flushed to Parquet by scheduled compaction.
- Layers are schemas: `raw` (as received), `clean` (typed, deduplicated, flagged), `curated`
  (dimensional and assessment marts), `serve` (API and export views).
- Snapshots are kept 30 days for time travel; expiry and compaction run nightly.

## Consequences

- A commit is one SQL transaction; no small-file explosion at 10-minute cadence.
- Time travel answers "what did the platform know at time t?".
- DuckLake is younger than Iceberg; an Iceberg export (stretch S6) keeps data portable.
- A spike in M1 confirms dbt-duckdb and dlt behaviour against an attached DuckLake catalog.

## Alternatives considered

- **Apache Iceberg with Lakekeeper:** the most portable choice, but more services and compaction
  work for a small, write-often workload.
- **TimescaleDB:** good for time series, but key features are under the Timescale License.
- **Plain Parquet files:** no transactions or snapshots.
