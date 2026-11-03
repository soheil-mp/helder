# ADR-0006: Kafka 4 with a schema registry and CloudEvents as the event backbone

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Observations arrive from pollers, backfills and revision jobs, and are consumed by quality
control, the lakehouse writer, the SensorThings loader and the alert engine, each at its own
pace. New QC rules must be replayable over past data. Volumes are small (tens of thousands of
events a day), but ordering per series, durability and replay matter.

## Decision

- **Apache Kafka 4.4 in KRaft mode** is the event log; one broker in Compose, three on
  Kubernetes through Strimzi.
- **Topics** (AsyncAPI 3.1 documented, `helder.<domain>.<event>.v<major>`):
  `helder.obs.raw.v1` (as received, keyed by series ID), `helder.obs.qc.v1` (with flags),
  `helder.obs.revision.v1`, `helder.registry.series.v1` and `helder.registry.station.v1`
  (compacted), `helder.alert.v1`, and one dead-letter topic per consumer group.
- **Envelope:** CloudEvents 1.0 in binary content mode (Kafka headers carry `ce_*` attributes);
  the payload is Avro with schemas in **Apicurio Registry 3** (Confluent-compatible API),
  `BACKWARD_TRANSITIVE` compatibility.
- **Keys** are stable series IDs, so all values of a series land in one partition, in order.
- **Delivery:** idempotent producers; consumers commit after their side effect; the stream
  processor runs exactly-once (Kafka transactions).

## Consequences

- Any consumer can be rebuilt by replaying topics; retention is 14 days on raw topics and
  infinite (compacted) on registries, within the storage budget.
- One more service to operate; mitigated by Compose health checks, Strimzi on Kubernetes and
  consumer lag SLOs.

## Alternatives considered

- **NATS JetStream:** lighter, but a smaller connector and schema ecosystem.
- **Redpanda:** Kafka-compatible and fast, but the Business Source License is outside the
  licence policy.
- **PostgreSQL as a queue:** enough for the volume, but no replay semantics or consumer groups.
