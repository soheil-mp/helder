# ADR-0012: QARTOD tests and flags for sensor quality control

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Raw RWS sensor data contains impossible values, spikes, frozen sensors, duplicates and time
errors ([domain research §8](../research/01-water-quality-domain.md#8-sensor-quality-control)).
Users need to see which values to trust, and every flag must be explainable.

## Decision

- Apply the U.S. IOOS **QARTOD** tests per series: syntax and time checks, gross range (sensor
  and user limits), climatology (per station and month), spike, rate of change, flat line, gap,
  and multi-depth consistency where a station measures at several heights.
- Use QARTOD flag values: **1** pass, **2** not evaluated, **3** suspect, **4** fail,
  **9** missing. The aggregate flag of a value is the worst of its test flags.
- Every flag records the rule ID, rule-set version and parameters; thresholds live in versioned
  YAML per observed property and station, reviewed like code.
- `ioos_qc` 3.0 is the reference implementation: Helder's streaming implementations are tested
  for equality with `ioos_qc` on the same inputs.
- RWS's own `Kwaliteitswaardecode` and `Statuswaarde` are kept alongside, never overwritten.
- Flagged values are never deleted; marts and alerts use only flags 1 and 2 by default.

## Consequences

- Transparent, standard quality information in every API response and export.
- Climatology limits need history; until enough exists, the test returns "not evaluated".
- Agreement between Helder's flags and RWS's later validation is measured in M26.
