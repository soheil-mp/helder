# Set up a development environment

This tutorial takes you from a fresh clone to a green `just check` in about ten minutes.

## 1. Install the tools

You need [uv](https://docs.astral.sh/uv/) 0.13 and [just](https://just.systems/) 1.59.
Docker is needed from milestone M1 onward.

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh   # or your package manager
uv tool install rust-just
```

Alternatively, open the repository in the devcontainer (`.devcontainer/devcontainer.json`),
which installs both and runs `just setup` for you.

## 2. Clone and set up

```sh
git clone https://github.com/soheil-mp/helder.git
cd helder
just setup
```

`just setup` creates a Python 3.13 environment from `uv.lock` with all eleven workspace
packages and the development tools, and installs the git hooks (secret scanning, linters,
Conventional Commit messages).

## 3. Run the checks

```sh
just check
```

This runs, in the same order as CI:

1. Ruff lint and format checks.
2. import-linter contracts: the package boundaries, and no I/O in `helder-core`, `helder-qc`
   and `helder-norms`.
3. The dependency policy: allowed licences only, and no ML libraries or model clients.
4. mypy in strict mode.
5. The test suite with branch coverage (at least 85 %).

## 4. Configure local settings

```sh
cp .env.example .env
```

Every setting has a placeholder in `.env.example`; see
[environment variables](../reference/environment.md). Never commit `.env`.

## Next

Read [live chloride at drinking water intakes](read-live-chloride.md) to see the data Helder
is built around.
