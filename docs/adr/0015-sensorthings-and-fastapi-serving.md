# ADR-0015: OGC SensorThings for observations, FastAPI for derived products

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Two kinds of consumers exist: those who want harmonised observations (series, values, flags) in
a standard form, ideally with live updates, and those who want Helder's judgements (status per
water body or intake, exceedances, bathing classifications, travel times, alerts).

## Decision

- **Observations:** serve through the **OGC SensorThings API 1.1** using **FROST-Server 2.8**
  (the reference implementation, LGPL-3.0, run as an unmodified container) on PostgreSQL with
  PostGIS. A loader maps stations to Things and Locations, series to Datastreams, Aquo
  properties to ObservedProperties, and QC flags to `resultQuality`. FROST's **MQTT** extension
  pushes new observations to subscribers.
- **Derived products:** a **FastAPI** service (`helder-api`) with versioned routes (`/v1/...`),
  OpenAPI 3.1, RFC 9457 problem details, cursor pagination, ETags and cache headers, rate
  limits, and attribution metadata in every response. It reads `serve` views through DuckDB.
- Both are read-only; there are no user accounts.

## Consequences

- Standard clients (QGIS SensorThings plugin, STA libraries) work with Helder's data.
- Two services to run; they share the registry and the stable series IDs.
- FROST-Server is Java; its resource needs are measured in M19.
