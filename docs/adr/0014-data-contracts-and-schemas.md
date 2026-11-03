# ADR-0014: Data contracts and schemas change before code

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Helder consumes external sources it does not control and publishes datasets, events and APIs
for others. Breaking changes in either direction must be caught before they reach users.

## Decision

- **Inbound:** each connector has a Pydantic model and a JSON Schema for the raw payload;
  recorded fixtures and a nightly live contract check validate them.
- **Events:** Avro schemas in `schemas/avro/`, registered in Apicurio with
  `BACKWARD_TRANSITIVE` compatibility, documented in an AsyncAPI 3.1 file.
- **Datasets:** every published table has an **Open Data Contract Standard 3.2** contract in
  `contracts/` (schema, semantics, quality rules, SLAs, terms and attribution), linted and
  tested with `datacontract-cli` in CI against the dbt marts.
- **APIs:** OpenAPI 3.1 generated from code, checked for breaking changes in CI (oasdiff) and
  fuzzed with Schemathesis.
- Contracts and schemas change in the same pull request as, and before, the code that uses them;
  breaking changes bump the major version and run side by side for a deprecation period.

## Consequences

- Consumers can rely on documented, versioned interfaces.
- More files to maintain; generators keep docs in sync.
