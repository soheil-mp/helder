# Environment variables

Helder reads its settings from environment variables; `.env.example` lists every one with a
placeholder. Copy it to `.env` for local work and never commit `.env`.

| Variable | Default in `.env.example` | Purpose |
| :-- | :-- | :-- |
| `HELDER_RWS_CLIENT_ID` | `helder-local-dev` | Value of the optional `X-API-KEY` header that identifies Helder to Rijkswaterstaat. A project name, never a personal e-mail address |
| `HELDER_HTTP_USER_AGENT` | `helder/0.0 (+https://github.com/soheil-mp/helder)` | User agent for every outgoing request |
| `HELDER_DATA_DIR` | `./data` | Local data directory (ignored by Git) |
| `HELDER_STORAGE_BUDGET_MIB` | `2048` | Total storage budget; the guard fails closed above it ([ADR-0003](../adr/0003-small-data-by-design.md)) |
| `HELDER_DOWNLOAD_BUDGET_MIB_PER_DAY` | `200` | Total download budget per day across sources |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | placeholders | Local PostgreSQL (DuckLake catalog) |
| `S3_ENDPOINT`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_BUCKET` | placeholders | Local S3-compatible object storage |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Kafka brokers |
| `SCHEMA_REGISTRY_URL` | `http://localhost:8081/apis/ccompat/v7` | Apicurio Registry (Confluent-compatible API) |
| `DAGSTER_HOME` | `./.dagster` | Dagster instance directory |
| `NTFY_BASE_URL`, `NTFY_TOPIC` | local placeholders | Anonymous alert push ([ADR-0016](../adr/0016-alerts-cap-and-cloudevents.md)) |

From M2.10 on, settings are validated at start-up and a test keeps this table, `.env.example`
and the code in sync.
