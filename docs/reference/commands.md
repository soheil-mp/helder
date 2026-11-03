# Commands

Run `just` to list every recipe. The main ones:

| Command | What it does |
| :-- | :-- |
| `just setup` | Create the environment from `uv.lock` and install the git hooks |
| `just fmt` | Format code and apply safe lint fixes |
| `just lint` | Ruff, formatting, import boundaries and the dependency policy |
| `just deps` | Dependency licences and the no-ML policy only |
| `just typecheck` | mypy in strict mode |
| `just test [args]` | Default test suite with coverage; arguments go to pytest |
| `just test-live` | Opt-in tests that call public sources |
| `just check` | Everything CI checks, in the same order |
| `just hooks` | Every pre-commit hook on every file |
| `just docs` / `just docs-build` | Serve or build this site |
| `just budget` | Show the configured data budgets |
| `just chloride [args]` | Live chloride at drinking water intakes ([tutorial](../tutorials/read-live-chloride.md)) |
| `just roadmap-sync [args]` | Mirror `ROADMAP.md` to GitHub issues ([how-to](../how-to/sync-roadmap-issues.md)) |
| `just repo-settings [args]` | Apply the GitHub settings ([how-to](../how-to/apply-repository-settings.md)) |
| `just up` / `just down` / `just e2e` | Local platform and end-to-end test (from M1) |
| `just clean` | Remove caches and build output |
