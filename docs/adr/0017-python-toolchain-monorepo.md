# ADR-0017: Python 3.13 uv monorepo with strict tooling

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Many packages share models and code (core types, QC, connectors, stream processor, pipelines,
API). They should version and test together, with clear dependency directions.

## Decision

- One repository, one **uv workspace** in `packages/`, one `uv.lock`:
  `helder-core` (types, units, time, registry models), `helder-qc` (QC and physics, pure),
  `helder-norms` (norm registry and evaluation, pure), `helder-connectors` (sources),
  `helder-stream` (Quix Streams apps), `helder-lake` (DuckLake I/O), `helder-pipelines`
  (Dagster definitions), `helder-api` (FastAPI), `helder-sta` (SensorThings loader),
  `helder-alerts` (alert engine), `helder-cli` (operator CLI).
- Dependency rules enforced by import-linter: pure packages (`core`, `qc`, `norms`) import no
  I/O packages; nothing imports `pipelines` or `api`.
- **Python 3.13** (pinned in `.python-version`) because `dagster-dbt` requires `<3.14`.
- Ruff (broad rule set), `mypy --strict`, pytest with Hypothesis and branch coverage
  (fail under 85 %), `just` as the task runner, `mise` for tool versions, a devcontainer.
- SQL in `transform/` (dbt), web app in `web/` (pnpm), infrastructure in `deploy/`.

## Consequences

- Atomic changes across packages; one CI pipeline.
- The workspace must stay fast: tests are split by marker (unit, integration, e2e, live).
