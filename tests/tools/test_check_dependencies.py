"""The dependency policy rejects ML packages and non-permissive licences."""

from email.message import Message
from importlib.metadata import Distribution
from os import PathLike
from pathlib import Path

import pytest

from tools import check_dependencies as cd


class FakeDist(Distribution):
    """A distribution with hand-made metadata."""

    def __init__(self, **fields: str | list[str]) -> None:
        self._meta = Message()
        for key, value in fields.items():
            for item in value if isinstance(value, list) else [value]:
                self._meta[key.replace("_", "-")] = item

    @property
    def metadata(self) -> Message:  # type: ignore[override]
        return self._meta

    def read_text(self, filename: str) -> str | None:  # noqa: ARG002
        return None

    def locate_file(self, path: str | PathLike[str]) -> Path:
        return Path(path)


@pytest.mark.parametrize(
    "name",
    ["torch", "scikit-learn", "scikit_learn", "OpenAI", "langchain-core", "qdrant-client"],
)
def test_ml_packages_are_out_of_scope(name: str) -> None:
    assert cd.scope_violation(name) is not None


@pytest.mark.parametrize("name", ["numpy", "duckdb", "httpx", "ioos-qc", "gsw", "dlt"])
def test_ordinary_packages_are_in_scope(name: str) -> None:
    assert cd.scope_violation(name) is None


def test_proprietary_packages_are_rejected() -> None:
    assert "proprietary" in (cd.scope_violation("soda-core") or "")


@pytest.mark.parametrize(
    ("expression", "allowed"),
    [
        ("MIT", True),
        ("Apache-2.0 OR MIT", True),
        ("GPL-3.0-only OR MIT", True),
        ("MIT AND BSD-3-Clause", True),
        ("Apache-2.0 WITH LLVM-exception", True),
        ("GPL-3.0-only", False),
        ("AGPL-3.0-or-later", False),
        ("MIT AND GPL-2.0-only", False),
        ("", False),
    ],
)
def test_spdx_expressions(expression: str, *, allowed: bool) -> None:
    assert cd.spdx_allowed(expression) is allowed


def test_licence_from_expression_free_text_and_classifier() -> None:
    assert cd.licence_of(FakeDist(Name="a", License_Expression="MIT")) == "MIT"
    assert cd.licence_of(FakeDist(Name="b", License="MIT License")) == "MIT"
    classified = FakeDist(
        Name="c", Classifier=["License :: OSI Approved :: Apache Software License"]
    )
    assert cd.licence_of(classified) == "Apache-2.0"
    assert cd.licence_of(FakeDist(Name="d")) is None


def test_check_verdicts() -> None:
    assert cd.check(FakeDist(Name="torch", License_Expression="BSD-3-Clause")).ok is False
    assert cd.check(FakeDist(Name="lib", License_Expression="GPL-3.0-only")).ok is False
    assert cd.check(FakeDist(Name="lib", License_Expression="MIT")).ok is True
    assert cd.check(FakeDist(Name="helder-core")).ok is True
    assert cd.check(FakeDist(Name="mystery")).reason == "licence metadata not recognised"


def test_lock_mode_reads_package_names() -> None:
    lock = '[[package]]\nname = "numpy"\n\n[[package]]\nname = "Torch"\n'
    verdicts = {v.name: v.ok for v in cd.check_lock(lock)}
    assert verdicts == {"numpy": True, "torch": False}


def test_report_exit_code(capsys: pytest.CaptureFixture[str]) -> None:
    ok = cd.Verdict("a", "MIT", ok=True)
    bad = cd.Verdict("b", "-", ok=False, reason="nope")
    assert cd.report([ok], verbose=True) == 0
    assert cd.report([ok, bad], verbose=False) == 1
    assert "FAIL b" in capsys.readouterr().out


def test_the_workspace_itself_passes() -> None:
    assert cd.main(["--lock"]) == 0
    assert cd.main([]) == 0
