# ADR-0007: Quix Streams with a shared, pure QC library

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Quality control must run in real time on arriving values and identically in backfills and
reprocessing. The spike, rate-of-change and flat-line tests need a little per-series state (the
last few values). Logic that is implemented twice drifts apart.

## Decision

- QC and derived physics live in **`helder-qc`**, a pure Python package with no I/O: functions
  take a series window and configuration and return flags with rule IDs. It has no dependency
  on Kafka, Dagster or databases (enforced by import-linter).
- The real-time processor is a **Quix Streams 3** application that keeps per-series windows in
  RocksDB state, calls `helder-qc`, and writes to `helder.obs.qc.v1` with exactly-once
  processing.
- Batch reprocessing (Dagster) calls the same functions on DuckDB query results.
- A **parity test** runs one recorded day through both paths and requires identical flags.

## Consequences

- One implementation of every rule; QC changes ship once.
- Python throughput is far beyond the needed rate (hundreds of events a minute).
- Quix Streams pins some dependencies (pydantic, confluent-kafka); Renovate groups updates.

## Alternatives considered

- **Apache Flink 2.3 / PyFlink:** the strongest stateful engine, but JVM-heavy for a laptop,
  and Python UDFs would still need the same library.
- **RisingWave:** streaming SQL is elegant for aggregations but awkward for QARTOD tests.
