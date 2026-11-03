# Helder

*Helder* is Dutch for "clear". Helder is an open data platform that watches water quality in
the Netherlands in near real time. It collects public sensor and laboratory data about rivers,
lakes, the coast, bathing sites, groundwater and drinking water. It checks every value with
standard quality tests and judges it against the right legal norm, citing the source. It
publishes the results as open APIs, alert feeds and a public dashboard.

> **Status:** planning complete, implementation starting. The research, architecture,
> decisions and a roadmap of 1,049 hours are in this repository; one example already reads
> live data. See [Status and plans](#status-and-plans).

## Why

Dutch water data is excellent but scattered. Rijkswaterstaat publishes 10-minute sensor
readings, RIVM publishes drinking water quality per pumping station, the EEA classifies bathing
waters, and the national subsurface register holds groundwater analyses. Each uses its own
format, vocabulary and rhythm. Real-time readings are published unvalidated: on the day this
project started, one oxygen sensor reported 1036.9 mg/l, about a hundred times what water can
hold. The legal yardsticks are just as spread out: annual means, daily means, log-percentiles,
values that apply only at drinking water intakes, and rules that changed on 12 January 2026.

Helder brings this together and makes it explainable:

- **Checked data.** Every sensor value gets QARTOD quality flags (gross range, climatology,
  spike, rate of change, flat line and more) plus physical cross-checks, such as salinity from
  conductivity with TEOS-10 and oxygen solubility. One shared library runs both in the stream
  and in backfills.
- **Norms as code.** Each yardstick is versioned data with its value, aggregation rule, legal
  force, validity dates and citation. Examples: the Bkl standards, the Drinkwaterbesluit
  (including the 2026 PFAS limits), the chloride agreements for intakes, the Bathing Water
  Directive and the RIVM cyanobacteria protocol.
- **Source to tap.** Rivers and their upstream gauges are linked to the 23 drinking water
  intakes, then to pumping stations, then to supply areas, with live salt-intrusion status at
  the intakes.
- **Never lose history.** Observations are bitemporal, so every alert can be explained later,
  even after Rijkswaterstaat has revised the values it was based on.
- **Indicative early warning.** Travel times from upstream stations to intakes are computed
  with a simple, open advection model in the spirit of the Rhine Alarm Model.
- **No machine learning.** Every output comes from a rule, an equation or a cited norm.

## Who it's for

- **Curious residents, swimmers and journalists** who want to see, with sources, what the water
  near them is doing. Helder is informational and links to the authorities that give advice.
- **Researchers and students** who need harmonised, quality-flagged Dutch water data through
  standard interfaces (OGC SensorThings, OGC API Features, Parquet exports).
- **Data and platform engineers** who want a complete, real-world reference for streaming
  ingestion, lakehouse design, orchestration, data contracts, data quality and GitOps at a
  laptop-friendly scale.

## Built with

| Area | Tools |
| :-- | :-- |
| Language and tooling | Python 3.13, uv workspace, Ruff, mypy (strict), pytest, Hypothesis, just, pre-commit |
| Ingestion | Async pollers (httpx, stamina), dlt for batch sources, recorded fixtures and a fake RWS service |
| Streaming | Apache Kafka 4 (KRaft), Apicurio Registry, Avro, CloudEvents, AsyncAPI, Quix Streams |
| Quality control | QARTOD tests (ioos_qc as reference), TEOS-10 (gsw), Pandera, Open Data Contract Standard 3.2 |
| Lakehouse | DuckLake 1.0, DuckDB 2.0, PostgreSQL 18, RustFS (S3-compatible) |
| Orchestration and SQL | Dagster 1.13, dbt-core 1.12 with dbt-duckdb, SQLFluff, OpenLineage |
| Serving | FROST-Server (OGC SensorThings API with MQTT), FastAPI, CAP 1.2 feeds, ntfy |
| Web | SvelteKit, MapLibre GL JS, DuckDB-WASM, Observable Plot, GitHub Pages |
| Operations | Docker, k3d, Helm, Argo CD, Strimzi, CloudNativePG, KEDA, Kyverno, SOPS, OpenTofu |
| Observability | OpenTelemetry, Prometheus, Grafana, Loki, Tempo, Pyrra SLOs |
| Supply chain | GitHub Actions pinned by SHA, Renovate, gitleaks, Syft SBOMs, Trivy, cosign, SLSA provenance |

Why each tool was chosen, with versions and licences:
[technology landscape](docs/research/03-technology-landscape.md).

## How to run it

The platform is being built; today you can run the research example, which reads live chloride
values at drinking water intakes from Rijkswaterstaat. It uses only the Python standard
library and downloads a few kilobytes.

```sh
git clone https://github.com/soheil-mp/helder.git
cd helder
python3 examples/latest_chloride.py          # sensors within 1.5 km of a drinking water intake
python3 examples/latest_chloride.py --all    # every chloride series updated in the last hour
```

For development you need [uv](https://docs.astral.sh/uv/) and [just](https://just.systems/)
(or open the repository in the devcontainer, which has both):

```sh
just setup                    # Python 3.13 workspace, dev tools and git hooks
just check                    # lint, import boundaries, strict types and tests, as in CI
cp .env.example .env          # local settings; never commit .env
just                          # list every task
```

Once the walking skeleton lands (M1), `just up` starts the local platform with Docker Compose
and `just e2e` runs the end-to-end test.

## Data sources and attribution

| Source | What Helder uses |
| :-- | :-- |
| [Rijkswaterstaat](https://rijkswaterstaatdata.nl/waterdata/) WaterWebservices and Geoservices | 10-minute sensor data, laboratory chemistry, bathing water microbiology, station catalogue |
| [RIVM](https://data.rivm.nl/geo/wfs) | Drinking water quality per pumping station, intakes, supply areas, protection zones |
| [EEA](https://www.eea.europa.eu/) | Official bathing water classifications |
| [PDOK](https://www.pdok.nl/) and [BRO](https://www.broloket.nl/) | Locations, networks, water board areas, treatment plants, groundwater analyses |
| [PEGELONLINE](https://www.pegelonline.wsv.de/) | Rhine discharge upstream of the Netherlands |
| [Open-Meteo](https://open-meteo.com/) | Rainfall context |

Every API response, export and dashboard view names its sources and retrieval times. Details,
terms and verified behaviour: [data sources](docs/research/02-data-sources.md). Helder does not
give swimming, drinking or health advice; for that, see the provinces (zwemwater.nl), your
drinking water company and RIVM.

## Documentation

- [Domain research](docs/research/01-water-quality-domain.md): who measures what, the legal
  norms, parameters, physics, statistics and observed data problems.
- [Data sources](docs/research/02-data-sources.md): endpoints verified against the live
  services, sizes, terms and pitfalls.
- [Technology landscape](docs/research/03-technology-landscape.md): choices, versions,
  licence policy and the no-ML dependency rule.
- [Architecture](docs/architecture.md) and [architecture decision records](docs/adr/README.md).
- [Roadmap](ROADMAP.md): 28 milestones, each with goals, items, estimates and exit criteria.

## Status and plans

Done:

- Research verified against the live services on 2026-11-03, including measured response
  sizes, time-zone pitfalls and how many intakes have a live sensor nearby.
- Twenty architecture decision records and the target architecture.
- Repository hygiene: secret scanning, linting and Conventional Commits in pre-commit, plus
  repository settings and roadmap issues as code.
- A working example that reads live data within a strict size budget.

Next: the engineering foundations (M0.5–M0.13), then the walking skeleton (M1), which carries
one real signal from Rijkswaterstaat through Kafka, quality control, DuckLake, dbt and the API
to a chart. All work ahead is in [ROADMAP.md](ROADMAP.md) and the
[open issues](https://github.com/soheil-mp/helder/issues).

## License

MIT, see [LICENSE](LICENSE). Data remains under the terms of its sources.
