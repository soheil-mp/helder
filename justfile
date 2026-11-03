# Helder task runner. Run `just` to list the recipes.
# Install just with `uv tool install rust-just` (or your package manager).

set shell := ["bash", "-euo", "pipefail", "-c"]
set dotenv-load := false

# List the available recipes
default:
    @just --list --unsorted

# Install the workspace, development tools and git hooks
setup:
    uv sync
    uv run pre-commit install --hook-type pre-commit --hook-type commit-msg

# Format code and apply safe lint fixes
fmt:
    uv run ruff format .
    uv run ruff check --fix .

# Lint, check formatting, import boundaries and the dependency policy
lint: deps
    uv run ruff check .
    uv run ruff format --check .
    uv run lint-imports

# Check dependency licences and the no-ML policy (ADR-0002)
deps:
    uv run python -m tools.check_dependencies --lock
    uv run python -m tools.check_dependencies

# Type-check everything in strict mode
typecheck:
    uv run mypy

# Run the default test suite with coverage; extra arguments go to pytest (`just test -k time`)
test *args:
    uv run pytest --cov --cov-report=term-missing -m "not integration and not e2e and not live" {{ args }}

# Run the opt-in tests that call public sources over the internet
test-live *args:
    uv run pytest -m live {{ args }}

# Run every pre-commit hook on every file
hooks:
    uv run pre-commit run --all-files

# Everything CI checks, in the same order
check: lint typecheck test

# Show the configured data budgets (ADR-0003)
budget:
    @grep -E '^HELDER_.*BUDGET' .env 2>/dev/null || grep -E '^HELDER_.*BUDGET' .env.example

# Print live chloride values at drinking water intakes (a few kilobytes from Rijkswaterstaat)
chloride *args:
    python3 examples/latest_chloride.py {{ args }}

# Start the local platform with Docker Compose
up:
    @echo "Not available yet: the Compose platform arrives in roadmap item M1.3." >&2
    @exit 1

# Stop the local platform
down:
    @echo "Not available yet: the Compose platform arrives in roadmap item M1.3." >&2
    @exit 1

# Poll, check, store and query one signal end to end against the fake RWS service
e2e:
    @echo "Not available yet: the end-to-end test arrives in roadmap item M1.12." >&2
    @exit 1

# Preview the GitHub issue changes implied by ROADMAP.md (add --apply to make them)
roadmap-sync *args:
    python3 scripts/sync_roadmap_issues.py {{ args }}

# Apply the repository's GitHub settings (see the script for --with-pages and --with-ci)
repo-settings *args:
    scripts/repo-settings.sh {{ args }}

# Remove caches and build output
clean:
    rm -rf .mypy_cache .pytest_cache .ruff_cache .import_linter_cache .hypothesis .coverage coverage.xml htmlcov dist build site
    find . -type d -name __pycache__ -not -path "./.venv/*" -prune -exec rm -rf {} +
