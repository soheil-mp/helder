# Add a dependency

1. Add it to the package that needs it, not to the workspace root:

    ```sh
    uv add --package helder-connectors httpx
    ```

    Development-only tools go into the root `dev` group: `uv add --dev <tool>`.

2. Check the policy:

    ```sh
    just deps
    ```

    The check fails on licences outside the allowlist and on any machine-learning library,
    model runtime, model-API client or vector database
    ([technology landscape §4–5](../research/03-technology-landscape.md#4-licence-policy-for-dependencies)).
    If a package has unusable licence metadata but an acceptable licence, add it to
    `EXCEPTIONS` in `tools/check_dependencies.py` with the licence, the version checked and
    the date.

3. Check the boundaries: `just lint` runs import-linter. Pure packages (`helder-core`,
   `helder-qc`, `helder-norms`) may not import I/O libraries.

4. Commit `pyproject.toml` and `uv.lock` together with a `build(deps):` message. Renovate keeps
   the version current from then on.
