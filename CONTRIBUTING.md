# Contributing to Helder

Thank you for helping. Helder turns public Dutch water quality data into checked, explained,
real-time information. This guide covers how to set up, how work is organised, and the rules
every change follows.

## Before you start

- Read [ROADMAP.md](ROADMAP.md): every planned piece of work is an item there and an issue on
  GitHub. Comment on the issue before starting so work is not duplicated.
- Read the [scope boundaries in CLAUDE.md](CLAUDE.md#scope-boundaries). In short: no machine
  learning or model APIs, no personal data, no user accounts, no secrets, small data, and
  every source used within its terms.
- For anything that changes a recorded decision, read the relevant
  [ADR](docs/adr/README.md) first.

## Set up

You need [uv](https://docs.astral.sh/uv/), [just](https://just.systems/) and Docker (Docker from
M1 on). The devcontainer has all of them.

```sh
just setup     # Python 3.13 workspace, dev tools and git hooks
just check     # lint, import boundaries, dependency policy, strict types and tests
just           # every other task
```

## How work flows

1. Pick an issue (or open one with the matching form: bug, feature, spike or data issue).
2. Branch from `main`: `m4.5-gap-backfill`, `fix-wfs-timezone`, ...
3. Change contracts and schemas first, then code, then tests and docs.
4. Commit in small working steps with [Conventional Commits](https://www.conventionalcommits.org/)
   (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `perf:`, `build:`, `ci:`, `chore:`). A hook
   checks the format. Use `build:` or `chore:` for tooling.
5. Open a pull request with the template. CI must pass ("CI passed"); merges use merge commits.
6. If the change completes a roadmap item, tick it in `ROADMAP.md` in the same pull request.

Never rewrite published history: no force-pushes, no squashing or rebasing of pushed commits.

## Code standards

- Python 3.13, typed throughout; `mypy --strict` and Ruff (all rules) must pass.
- Package boundaries are enforced by import-linter: `helder-core`, `helder-qc` and
  `helder-norms` stay free of I/O.
- Times are UTC inside Helder; convert at the edge and test it. Units are explicit.
- Every QC test, physical equation and norm cites its source and has a worked-example test.
- Tests never call live services. Use recorded fixtures or the fake RWS service; live checks
  are marked `live` and run only on request (`just test-live`).
- Property-based tests (Hypothesis) for conversions, parsers and invariants.

## Data rules

- Never commit data. Small recorded fixtures under `tests/fixtures/` are the only exception;
  strip headers and trim them to what the test needs.
- Respect the budgets in [ADR-0003](docs/adr/0003-small-data-by-design.md): filter at the
  source, never download whole layers or archives.
- Keep attribution intact: every output names its sources and retrieval time.

## Documentation

Docs follow the Diátaxis structure (tutorials, how-to guides, reference, explanation) and are
built with Zensical (`just docs`). Significant decisions get an ADR in `docs/adr/`.

## Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Report security problems
privately, as described in [SECURITY.md](SECURITY.md).
