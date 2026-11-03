"""The workspace packages install, import and expose their version."""

import importlib
from importlib.metadata import version

import pytest

PACKAGES = [
    "core",
    "qc",
    "norms",
    "connectors",
    "lake",
    "stream",
    "sta",
    "alerts",
    "pipelines",
    "api",
    "cli",
]


@pytest.mark.parametrize("name", PACKAGES)
def test_package_imports_and_reports_its_version(name: str) -> None:
    module = importlib.import_module(f"helder_{name}")
    assert module.__version__ == version(f"helder-{name}")
    assert module.__doc__, "every package states its purpose in its docstring"
