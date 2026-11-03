# Working on Helder

Context for coding assistants and contributors. Read [ROADMAP.md](ROADMAP.md) for what to build
next and [docs/architecture.md](docs/architecture.md) for how the parts fit.

## Scope boundaries

Every change must stay inside these boundaries:

- **No machine learning or AI in the product.** No calls to model APIs, no local models,
  embeddings or ML libraries, and no datasets for training or evaluating models. Processing is
  rule-based quality control, physics, classical statistics and cited norms
  ([ADR-0002](docs/adr/0002-deterministic-rule-based-processing.md)). No forecasting.
- **No personal data.** Only public environmental data and synthetic test data. Connectors keep
  fields through allowlists ([ADR-0020](docs/adr/0020-privacy-attribution-and-source-terms.md)).
  The RWS `X-API-KEY` header carries a project identifier, never an e-mail address. Fixtures,
  seeds, examples and screenshots contain no data about people. No scraping of data about
  people.
- **No user accounts** and no storing of other people's data. Alerts use anonymous channels
  (CAP feeds, ntfy topics, webhooks).
- **No security tooling** that finds or exploits vulnerabilities.
- **No secrets in code or history.** Read keys from environment variables; `.env` stays ignored;
  every new variable goes into `.env.example` with a placeholder.
- **Small data.** Filter at the source, follow the watchlist, respect the budgets in
  [ADR-0003](docs/adr/0003-small-data-by-design.md). Never request the unfiltered RWS latest
  layer (more than 325 MB). Data never goes into Git; only small recorded fixtures do.
- **Source terms and attribution.** A connector stays disabled until its terms are recorded in
  `reference/sources.yaml`. zwemwater.nl data is not used. Outputs name their sources and
  retrieval times.
- **Informational, not advisory.** Never phrase output as swimming, drinking or health advice;
  show legal force and source next to every judgement.
- **Licences.** The project is MIT. Only add dependencies whose licences allow that (see
  [technology landscape §4](docs/research/03-technology-landscape.md#4-licence-policy-for-dependencies)),
  and never copy code we do not have the right to share.

## Git workflow

- Commit after each working step with a Conventional Commit message (`feat:`, `fix:`, `docs:`,
  `chore:`, `test:`, `refactor:`, `ci:`, `build:`, `perf:`). Use `chore:` or `build:` for
  tooling so release-please does not propose a release too early.
- Never rewrite published history: no squashing, amending or rebasing pushed commits, and no
  force-push. Never change commit dates.
- Keep README.md and ROADMAP.md current when a change affects them; tick roadmap items when they
  are merged and run `python3 scripts/sync_roadmap_issues.py --apply`.

## Engineering conventions

- Python 3.13, uv workspace, Ruff, `mypy --strict`, pytest with Hypothesis
  ([ADR-0017](docs/adr/0017-python-toolchain-monorepo.md)).
- UTC everywhere inside Helder. RWS times carry `+01:00` all year; the RWS WFS layer labels MET
  times as `Z`. Convert at the edge and test it.
- Units are explicit: Pint quantities in Python and unit suffixes in names (`chloride_mg_l`,
  `conductivity_ms_m`). Bacteria counts are normalised to counts per 100 ml.
- Aquo codes identify observed properties ([ADR-0004](docs/adr/0004-aquo-and-sensorthings-data-model.md)).
- Every QC test, physics function and norm cites its source in its docstring or registry entry,
  and has a worked-example test. Norm values marked "to transcribe" may not be used until they
  are transcribed with a page reference and reviewed.
- `helder-core`, `helder-qc` and `helder-norms` stay free of I/O; import-linter enforces it.
- Schemas and data contracts change before the code that uses them
  ([ADR-0014](docs/adr/0014-data-contracts-and-schemas.md)).
- Tests never call live services; use recorded fixtures or the fake RWS service. Live checks
  are opt-in and run nightly.
- Significant decisions get an ADR in `docs/adr/`.
