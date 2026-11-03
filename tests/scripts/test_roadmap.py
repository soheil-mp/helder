"""ROADMAP.md stays machine-readable: the issue sync depends on its structure."""

import re
from pathlib import Path

import pytest

from scripts.sync_roadmap_issues import (
    Item,
    Milestone,
    issue_body,
    issue_title,
    item_labels,
    parse_roadmap,
)

ROADMAP = Path(__file__).resolve().parents[2] / "ROADMAP.md"


@pytest.fixture(scope="module")
def milestones() -> list[Milestone]:
    return parse_roadmap(ROADMAP.read_text(encoding="utf-8"))


def test_milestones_are_numbered_consecutively(milestones: list[Milestone]) -> None:
    numbered = [ms.id for ms in milestones if ms.id != "S"]
    assert numbered == [f"M{i}" for i in range(len(numbered))]


def test_items_are_numbered_consecutively_within_each_milestone(
    milestones: list[Milestone],
) -> None:
    for ms in milestones:
        if ms.id == "S":
            continue
        expected = [f"{ms.id}.{i}" for i in range(1, len(ms.items) + 1)]
        assert [item.id for item in ms.items] == expected


def test_every_milestone_has_a_goal_and_exit_criteria(milestones: list[Milestone]) -> None:
    for ms in milestones:
        if ms.id == "S":
            continue
        assert ms.goal, ms.id
        assert ms.exit_criteria, ms.id
        assert ms.goal.endswith("."), f"{ms.id} goal was cut off while parsing"


def test_estimates_are_plausible(milestones: list[Milestone]) -> None:
    for ms in milestones:
        for item in ms.items:
            assert 1 <= item.hours <= 16, item.id


def test_summary_table_matches_the_items(milestones: list[Milestone]) -> None:
    text = ROADMAP.read_text(encoding="utf-8")
    for ms in milestones:
        if ms.id == "S":
            continue
        row = re.search(rf"\| \[{ms.id} [^|]+\]\([^)]+\) \| (\d+) \| (\d+) \|", text)
        assert row, f"{ms.id} missing from the summary table"
        assert int(row.group(1)) == len(ms.items), ms.id
        assert int(row.group(2)) == sum(item.hours for item in ms.items), ms.id


def test_titles_fit_and_carry_the_id() -> None:
    item = Item("M9.9", 3, "Spike: " + "word " * 40, done=False)
    title = issue_title(item)
    assert title.startswith("M9.9 ")
    assert len(title) <= 90


def test_labels_reflect_size_and_kind() -> None:
    assert item_labels(Item("M1.6", 5, "Spike: something", done=False)) == [
        "roadmap",
        "size:L",
        "type:spike",
    ]
    assert item_labels(Item("S2", 2, "Optional", done=False)) == [
        "roadmap",
        "size:S",
        "type:stretch",
    ]


def test_issue_bodies_link_absolutely_and_carry_the_marker(
    milestones: list[Milestone],
) -> None:
    ms = milestones[1]
    body = issue_body(ms.items[0], ms, "owner/repo")
    assert f"<!-- roadmap-id: {ms.items[0].id} -->" in body
    assert "](docs/" not in body
    assert f"https://github.com/owner/repo/blob/main/ROADMAP.md#{ms.anchor}" in body
