# Technology landscape and tool selection

*Versions, licences and activity were read from PyPI, GitHub and the projects' download pages
on 2026-11-03. Renovate keeps the pins current; this page records why each tool was chosen.*

## 1. What the platform needs

| Need | Consequence for the stack |
| :-- | :-- |
| About 600 live sensor series every 10 minutes, a few thousand laboratory results a day, a few hundred megabytes in total | Small data: an embedded analytical engine beats a cluster; every service must fit on a laptop next to the others |
| Late, revised and duplicated values | Event log with replay, idempotent writes, bitemporal storage with snapshots and time travel |
| The same quality checks live and in backfills | QC logic in one pure-Python library used by the stream processor and by batch jobs |
| Legal yardsticks with sources and validity dates | Norms as versioned data, evaluated in SQL and Python with tests per norm |
| Many public consumers, standard formats | OGC SensorThings API, OGC API Features, CAP alerts, OpenAPI, data contracts |
| One maintainer, months of work | Mainstream tools with strong docs, everything as code, CI that catches mistakes early |
| No ML anywhere | A dependency policy that blocks ML libraries and model clients ([ADR-0002](../adr/0002-deterministic-rule-based-processing.md)) |

## 2. Selected stack

| Layer | Choice (version) | Licence | Why | Alternatives considered |
| :-- | :-- | :-- | :-- | :-- |
| Language and packaging | Python **3.13**, uv 0.13 workspace | PSF, MIT/Apache-2.0 | One language for connectors, stream processing, QC, API and orchestration; uv gives fast, locked, reproducible environments. 3.13 because `dagster-dbt` 0.29.28 still requires `<3.14` | Python 3.14 (blocked by dagster-dbt), Poetry, Rye |
| Lint, format, types | Ruff 0.17, mypy 2.4 (`--strict`), import-linter 2.15 | MIT, MIT, BSD-2 | Industry defaults; import-linter enforces package boundaries | ty 0.0.x (still pre-release; tracked) , Pyright |
| Tests | pytest 9.2, Hypothesis 6.170, pytest-recording 0.14, Testcontainers 4.15, Schemathesis 4.33, Locust 2.47 | MIT, MPL-2.0, MIT, Apache-2.0, MIT, MIT | Unit, property, recorded-HTTP, integration, API-fuzz and load tests | VCR.py directly, k6 (AGPL) |
| HTTP clients | httpx 0.28 with stamina 26.1 retries | BSD-3, MIT | Async, HTTP/2, timeouts; retries with jitter and budgets | aiohttp, requests |
| Batch ingestion | dlt 1.32 (`ducklake` extra) | Apache-2.0 | Declarative REST and WFS sources, incremental cursors, schema contracts, a DuckLake destination | Airbyte (heavy), Meltano/Singer, hand-written loaders |
| Event backbone | Apache Kafka **4.4.0** (KRaft, no ZooKeeper) | Apache-2.0 | Durable, replayable log; compacted topics for registries; the lingua franca of streaming | NATS JetStream (lighter, smaller ecosystem), Redpanda (BSL), Pulsar (heavier) |
| Schema registry | Apicurio Registry 3.3 (Confluent-compatible API) | Apache-2.0 | Avro and JSON Schema with compatibility rules; also stores AsyncAPI documents | Karapace 6.2, Confluent Schema Registry (Confluent Community License) |
| Event format | CloudEvents 1.0.2 (`cloudevents` 2.2 SDK), AsyncAPI 3.1 | Apache-2.0 | Vendor-neutral envelope and machine-readable topic documentation | Bare JSON |
| Stream processing | Quix Streams 3.28 (exactly-once, RocksDB state) | Apache-2.0 | Pure Python, so the QC library runs unchanged in the stream and in backfills ([ADR-0007](../adr/0007-quix-streams-shared-qc-library.md)) | Apache Flink 2.3 / PyFlink (JVM, Python UDF overhead), RisingWave 3.1 (SQL only), Bytewax (stale) |
| Sensor QC | ioos_qc 3.0 (QARTOD) as reference; gsw 3.6 (TEOS-10) | Apache-2.0, BSD-3 | Community-standard tests and flags; seawater physics | Own implementations only |
| Dataframe validation | Pandera 0.35 | MIT | Typed schemas for pandas and Polars frames inside Python steps | Great Expectations 1.24 (heavier), Soda Core 4 (proprietary licence) |
| Lakehouse | **DuckLake 1.0** (April 2026) with DuckDB **2.0**, PostgreSQL 18 catalog, RustFS 1.0 object store | MIT, MIT, PostgreSQL, Apache-2.0 | SQL catalog, snapshots, time travel and *data inlining* of small inserts, which suits 10-minute micro-batches ([ADR-0008](../adr/0008-ducklake-lakehouse.md)) | Apache Iceberg 1.12 + Lakekeeper 0.14 (more moving parts, small-file compaction), Delta Lake, plain Parquet |
| Object storage | RustFS 1.0.4, fallback SeaweedFS 4.52 | Apache-2.0 | S3-compatible, single binary, permissive licence | MinIO (community repository archived in April 2026, AGPL), Garage (AGPL) |
| Orchestration | Dagster **1.13** with `dagster-dbt` | Apache-2.0 | Software-defined assets, partitions, sensors, asset checks, freshness and lineage in one UI ([ADR-0010](../adr/0010-dagster-orchestration.md)) | Airflow 3, Kestra 2.0, Prefect 3 |
| SQL transformations | dbt-core **1.12** with dbt-duckdb 1.11, SQLFluff 4.5 | Apache-2.0, Apache-2.0, MIT | Mature testing, contracts, unit tests and docs; first-class Dagster integration ([ADR-0011](../adr/0011-dbt-transformations.md)) | SQLMesh 0.236 (strong, but weaker Dagster integration), dbt Fusion engine (ELv2, not used) |
| Data contracts | Open Data Contract Standard **3.2**, datacontract-cli 1.2.9 | Apache-2.0, MIT | Contracts for every published dataset, linted and tested in CI ([ADR-0014](../adr/0014-data-contracts-and-schemas.md)) | dbt model contracts only |
| Lineage | OpenLineage 1.55 events from Dagster and dbt | Apache-2.0 | Open standard; viewable in Dagster and exportable | Marquez (last release October 2024), DataHub and OpenMetadata (heavy) |
| Sensor API | FROST-Server **2.8.2** (OGC SensorThings API 1.1 with MQTT) | LGPL-3.0, run as an unmodified container | The official reference implementation of the OGC standard for sensor observations, with live MQTT push ([ADR-0015](../adr/0015-sensorthings-and-fastapi-serving.md)) | Own SensorThings subset, pygeoapi EDR |
| Product API | FastAPI 0.162, Pydantic 2, Granian 2.8 | MIT, MIT, BSD-3 | Derived products (status, exceedances, alerts, travel times) with OpenAPI 3.1 | Litestar |
| Alerts | CAP 1.2 Atom feed, CloudEvents webhooks, ntfy 2.37 push | Apache-2.0 (ntfy) | Standard alert format plus anonymous push with no user accounts ([ADR-0016](../adr/0016-alerts-cap-and-cloudevents.md)) | E-mail (needs addresses: personal data) |
| Web app | SvelteKit 2 (static adapter), MapLibre GL JS 6.16, DuckDB-WASM, Observable Plot | MIT, BSD-3, MIT, ISC | A static site on GitHub Pages that queries Parquet snapshots in the browser ([ADR-0019](../adr/0019-static-dashboard-duckdb-wasm.md)) | Evidence (slower releases), Observable Framework (little activity since May 2026), Streamlit (needs a server) |
| Notebooks for validation | marimo 0.25 | Apache-2.0 | Reactive, stored as plain Python, reviewable in Git | Jupyter |
| Containers | Docker Buildx, Compose; Syft 1.56, Trivy 0.76, cosign 3.1 | Apache-2.0 | SBOMs, vulnerability gates and keyless signing for every image | Kaniko, Grype |
| Kubernetes | k3d 5.9, Helm, Argo CD 3.5, Strimzi 1.3, CloudNativePG 1.30, KEDA 2.21, Kyverno 1.19, SOPS 3.13 with age | MIT, Apache-2.0, MPL-2.0 | A local production-like cluster, GitOps, operators for Kafka and PostgreSQL, lag-based autoscaling, admission policies, encrypted secrets in Git ([ADR-0018](../adr/0018-kubernetes-gitops.md)) | kind, Flux 2.10, Kustomize only |
| Observability | OpenTelemetry SDK 1.45 and Collector 0.164, Prometheus 3.15, Grafana 13.3, Loki 3.7, Tempo 3.1, Pyrra 0.10 | Apache-2.0; Grafana, Loki and Tempo AGPL-3.0, run as unmodified services | Vendor-neutral telemetry, dashboards and SLOs as code | VictoriaMetrics 1.155 (also good), Sloth |
| Infrastructure as code | OpenTofu 1.13 | MPL-2.0 | Optional cloud demo and GitHub repository settings as code | Terraform (BSL) |
| Docs | Zensical 0.0.74, Diátaxis structure, MADR 4 ADRs, Mermaid C4 | MIT | The successor to Material for MkDocs from the same team | MkDocs Material 9.8 |
| CI/CD | GitHub Actions (pinned by SHA), release-please, Renovate, pre-commit, gitleaks, OpenSSF Scorecard | Apache-2.0 / MIT | Every check runs locally and in CI | — |

## 3. Decisions worth a second look

- **Kafka for 600 series?** The volume would fit in PostgreSQL. Kafka is chosen for what it
  makes possible: replaying history through new QC rules, decoupling slow consumers
  (SensorThings, lake, alerts), exactly-once processing and backpressure. A single KRaft broker
  uses a few hundred megabytes of memory in Compose; Strimzi runs it on Kubernetes.
- **DuckLake rather than Iceberg.** Both are open table formats with snapshots. DuckLake keeps
  metadata in PostgreSQL, so a micro-batch commit is one SQL transaction, and small inserts can
  be *inlined* in the catalog until compaction. Iceberg export is a stretch goal (S6) for
  interoperability.
- **Two APIs.** Raw observations are served by a standard (SensorThings) through its reference
  implementation; Helder's own logic (norms, statuses, alerts, travel times) is served by
  FastAPI. Neither duplicates the other.
- **Python 3.13 pin.** Revisit when `dagster-dbt` supports 3.14 (Renovate watches it).
- **Quix Streams pins** `pydantic<2.14` and `confluent-kafka<2.13`; the lock file resolves
  below those caps. Tracked in M6.

## 4. Licence policy for dependencies

The project is MIT. Dependencies must allow that ([ADR-0017](../adr/0017-python-toolchain-monorepo.md)):

| Licence | Allowed as a library | Allowed as a separate service |
| :-- | :-- | :-- |
| MIT, BSD-2/3, Apache-2.0, ISC, PSF, Zlib, Unlicense, CC0, 0BSD | Yes | Yes |
| MPL-2.0 (file-level copyleft) | Yes, unmodified | Yes |
| LGPL-2.1/3.0 | No | Yes, unmodified container (FROST-Server) |
| GPL, AGPL | No | Yes, unmodified container, never vendored or linked (Grafana, Loki, Tempo) |
| SSPL, BSL, ELv2, Commons Clause, Confluent Community License, proprietary | No | No |

`tools/check_dependencies.py` (M0.7) reads `uv.lock` and the web lock file, fails on any licence
outside the allowlist, and runs in pre-commit and CI.

## 5. No-ML deny-list

The same check fails if any of these appear anywhere in the dependency tree: model frameworks
(torch, tensorflow, keras, jax, flax, mxnet, onnxruntime), classical ML (scikit-learn, xgboost,
lightgbm, catboost, river, pyod, sktime, darts, prophet, tsfresh), NLP and embeddings
(transformers, sentence-transformers, spacy, gensim, huggingface-hub, tokenizers), model API
clients and frameworks (openai, anthropic, google-generativeai, google-genai, mistralai,
cohere, ollama, langchain*, llama-index*, litellm) and vector databases (qdrant-client,
weaviate-client, lancedb, chromadb, pinecone*). dlt is installed without its vector-database
extras.

## 6. Ecosystem changes that shaped choices

- **DuckLake 1.0** was published in April 2026 and DuckDB **2.0.0** on 2026-10-21.
- **Kafka 4.x** removed ZooKeeper; 4.4.0 is the newest release on the Apache download site.
- The **MinIO** community repository was archived on GitHub (last push 2026-04-24).
- **Marquez** has had no release since October 2024; OpenLineage itself is active.
- **Observable Framework** has had little activity since May 2026.
- **Soda Core 4** is published under a proprietary licence.
- **SQLMesh** now lives in the `SQLMesh/sqlmesh` organisation and remains Apache-2.0.
- **FROST-Server** implements SensorThings 1.1 and the drafts of SensorThings 2.0.
