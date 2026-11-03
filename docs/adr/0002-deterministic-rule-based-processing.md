# ADR-0002: Deterministic, rule-based processing; no machine learning

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Water quality judgements must be explainable to anyone who asks "why is this red?". Legal norms
are defined as rules over statistics (annual means, percentiles, daily means). Sensor quality
control has community standards (QARTOD) built from explicit tests. The project also has a hard
scope boundary: no AI or ML in the product.

## Decision

Every output is computed by an equation, a statistical procedure with a closed form, or a cited
rule table:

- Quality control: QARTOD tests with documented thresholds, physical consistency checks
  (TEOS-10 salinity, oxygen solubility), and explicit rules for duplicates and time stamps.
- Assessment: norms from legal or scientific sources, evaluated with the aggregation rule the
  source prescribes (for example the log10 percentile method of the Bathing Water Directive).
- Indications: transparent physics (advection travel time) and classical statistics
  (Mann–Kendall trend test, Sen's slope).

There is no forecasting, no learned anomaly detection, no clustering, no model inference and no
call to any model API. A dependency check blocks ML libraries and model clients
([technology landscape §5](../research/03-technology-landscape.md#5-no-ml-deny-list)).

## Consequences

- Every flag and status can be traced to a rule ID, its parameters and its source.
- Some patterns that ML might catch are missed; Helder states its tests and their limits
  instead.
- Thresholds need care and review; they live in versioned configuration with tests.

## Alternatives considered

- Statistical anomaly detection with learned models: rejected (scope and explainability).
