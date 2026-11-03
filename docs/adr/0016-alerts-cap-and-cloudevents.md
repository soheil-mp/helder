# ADR-0016: Alerts as CAP 1.2, CloudEvents and anonymous push

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Some situations deserve notification: a chloride daily mean above 200 mg/l at an intake, a
fast conductivity rise upstream of an intake, a QC failure across a station, a source outage.
Notifications must not create noise, must be explainable afterwards, and must not require
collecting contact details.

## Decision

- An **alert rule** combines a condition on curated data (norm exceedance, trend, QC state,
  freshness), a minimum duration, hysteresis for clearing, and a severity. Rules are YAML with
  tests, like norms.
- The engine is a state machine per rule and subject (`inactive → pending → firing →
  resolved`), suppresses alerts whose inputs are QC-flagged as failed, and deduplicates.
- Alerts are published as **OASIS CAP 1.2** messages in an Atom feed, as **CloudEvents** on
  `helder.alert.v1` and webhooks, and to **ntfy** topics that anyone can subscribe to without an
  account.
- Every alert stores the snapshot ID, rule version and the values it used (ADR-0009).
- Alert texts say that Helder is informational and link to the responsible authority.

## Consequences

- Standard consumers (CAP aggregators, feed readers, phones via ntfy) work without accounts.
- No personal data is collected.
