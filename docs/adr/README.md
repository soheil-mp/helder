# Architecture decision records

Decisions are recorded in the [MADR 4](https://adr.github.io/madr/) format. An ADR is never
edited after acceptance except to change its status; a new ADR supersedes it.

| ADR | Decision | Status |
| :-- | :-- | :-- |
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-deterministic-rule-based-processing.md) | Deterministic, rule-based processing; no machine learning | Accepted |
| [0003](0003-small-data-by-design.md) | Small data by design, with enforced budgets | Accepted |
| [0004](0004-aquo-and-sensorthings-data-model.md) | Aquo vocabulary inside an observations-and-measurements model | Accepted |
| [0005](0005-rws-polling-strategy.md) | Poll RWS with the WFS latest layer; backfill gaps with the API | Accepted |
| [0006](0006-kafka-event-backbone.md) | Kafka 4 with a schema registry and CloudEvents as the event backbone | Accepted |
| [0007](0007-quix-streams-shared-qc-library.md) | Quix Streams with a shared, pure QC library | Accepted |
| [0008](0008-ducklake-lakehouse.md) | DuckLake on PostgreSQL and S3-compatible storage | Accepted |
| [0009](0009-bitemporal-observations.md) | Bitemporal observations that keep every revision | Accepted |
| [0010](0010-dagster-orchestration.md) | Dagster for orchestration | Accepted |
| [0011](0011-dbt-transformations.md) | dbt-core for SQL transformations | Accepted |
| [0012](0012-qartod-quality-flags.md) | QARTOD tests and flags for sensor quality control | Accepted |
| [0013](0013-norms-as-code.md) | Norms as code, with legal provenance and validity dates | Accepted |
| [0014](0014-data-contracts-and-schemas.md) | Data contracts and schemas change before code | Accepted |
| [0015](0015-sensorthings-and-fastapi-serving.md) | OGC SensorThings for observations, FastAPI for derived products | Accepted |
| [0016](0016-alerts-cap-and-cloudevents.md) | Alerts as CAP 1.2, CloudEvents and anonymous push | Accepted |
| [0017](0017-python-toolchain-monorepo.md) | Python 3.13 uv monorepo with strict tooling | Accepted |
| [0018](0018-kubernetes-gitops.md) | Compose for development, Kubernetes with GitOps for production-like runs | Accepted |
| [0019](0019-static-dashboard-duckdb-wasm.md) | A static dashboard on GitHub Pages with DuckDB-WASM | Accepted |
| [0020](0020-privacy-attribution-and-source-terms.md) | Privacy, attribution and source terms by construction | Accepted |
