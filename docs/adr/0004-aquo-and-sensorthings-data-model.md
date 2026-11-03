# ADR-0004: Aquo vocabulary inside an observations-and-measurements model

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Dutch water data uses the Aquo standard (compartment, quantity, parameter, unit, condition,
quality codes). International consumers expect the ISO 19156 Observations and Measurements
model, which the OGC SensorThings API implements (Thing, Location, Datastream, Sensor,
ObservedProperty, FeatureOfInterest, Observation). Sources outside RWS (RIVM, BRO, EEA) use
their own field names.

## Decision

- The canonical model is observations-and-measurements: a **series** (Datastream) is identified
  by station, observed property, sampling height, procedure (sensor or method) and programme.
- Observed properties are identified by their **Aquo** codes (`CONCTTE`/`Cl`, `GELDHD`, ...),
  with English labels and units mapped to UCUM codes for the SensorThings representation.
- Units are handled with Pint and normalised per observed property (for example bacteria to
  counts per 100 ml).
- Each non-RWS source has an explicit mapping table to Aquo codes, versioned and tested.

## Consequences

- One vocabulary from ingestion to API; SensorThings loading is a mechanical mapping.
- Mapping tables need maintenance when sources add parameters (alerts on unmapped codes).
