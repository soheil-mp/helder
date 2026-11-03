# ADR-0001: Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Helder will be built over many months. Choices about sources, storage, processing and
standards interact, and the reasons behind them fade quickly.

## Decision

Record every significant decision as a numbered ADR in `docs/adr/`, using MADR 4: context,
decision, consequences and the alternatives considered. ADRs are immutable once accepted; a
change of mind is a new ADR that supersedes the old one. A pull request that changes a recorded
decision must add or supersede an ADR (part of the definition of done in ROADMAP.md).

## Consequences

- Reviewers and future contributors can see why, not only what.
- A small writing cost per decision.
