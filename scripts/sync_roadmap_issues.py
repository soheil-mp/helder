#!/usr/bin/env python3
"""Mirror ROADMAP.md into GitHub milestones, labels and issues.

ROADMAP.md is the source of truth. Every open roadmap item gets exactly one issue in the
milestone of the same name; ticked items close their issue. The script is idempotent: it finds
existing issues by a hidden marker in their body, so it can run after every roadmap change.

Usage:
    python3 scripts/sync_roadmap_issues.py                    # dry run: print the plan
    python3 scripts/sync_roadmap_issues.py --apply            # create and close what is needed
    python3 scripts/sync_roadmap_issues.py --apply --update   # also refresh existing bodies
    python3 scripts/sync_roadmap_issues.py --only M0,M1       # limit to some milestones
    python3 scripts/sync_roadmap_issues.py --include-stretch  # also mirror S1, S2, ...

Needs the GitHub CLI (``gh``) authenticated with write access. Standard library only, so it
runs before the Python workspace exists.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

ROADMAP = Path(__file__).resolve().parent.parent / "ROADMAP.md"
DEFAULT_REPO = "soheil-mp/helder"
MARKER = "<!-- roadmap-id: {id} -->"
MARKER_RE = re.compile(r"<!-- roadmap-id: ([MS]\d+(?:\.\d+)?) -->")
CREATE_DELAY_S = 1.2  # stay below GitHub's secondary rate limit for content creation
TITLE_MAX = 90
SHORT_CLAUSE = 24  # a first clause shorter than this is too vague as a title
SMALL_H, MEDIUM_H = 2, 4  # size label limits in hours
STRETCH = "Stretch goals"

PHASE_RE = re.compile(r"^## Phase (\d+): (.+)$")
MILESTONE_RE = re.compile(r"^### (M\d+) · (.+)$")
GOAL_RE = re.compile(r"^\*\*Goal:\*\* (.+)$")
EXIT_RE = re.compile(r"^\*\*Exit criteria:\*\* (.+)$")
ITEM_RE = re.compile(r"^- \[( |x)\] \*\*((?:M\d+\.\d+)|(?:S\d+))\*\* \((\d+) h\) (.+)$")

LABELS = {
    "roadmap": ("0e8a16", "Planned work mirrored from ROADMAP.md"),
    "type:spike": ("d4c5f9", "Answers a question and records the answer before dependent work"),
    "type:stretch": ("c2e0c6", "Optional work beyond the 1.0 scope"),
    "size:S": ("ededed", "Up to 2 hours"),
    "size:M": ("bfd4f2", "3 to 4 hours"),
    "size:L": ("5319e7", "5 hours or more"),
}


@dataclass
class Item:
    """One roadmap item such as M4.5 or S3."""

    id: str
    hours: int
    text: str
    done: bool


@dataclass
class Milestone:
    """One roadmap milestone and its items."""

    id: str
    title: str
    phase: str
    goal: str = ""
    exit_criteria: str = ""
    items: list[Item] = field(default_factory=list)

    @property
    def full_title(self) -> str:
        """The GitHub milestone title, for example 'M4 · Real-time RWS ingestion'."""
        return f"{self.id} · {self.title}" if self.id != "S" else STRETCH

    @property
    def anchor(self) -> str:
        """GitHub's heading anchor for this milestone in ROADMAP.md."""
        if self.id == "S":
            return "stretch-goals"
        slug = re.sub(r"[^\w\- ]", "", self.full_title.lower())
        return slug.replace(" ", "-")


def _continue(current: Milestone, field_name: str, line: str) -> None:
    """Append a wrapped continuation line to the field it belongs to."""
    extra = " " + line.strip()
    if field_name == "item":
        current.items[-1].text += extra
    elif field_name == "goal":
        current.goal += extra
    elif field_name == "exit":
        current.exit_criteria += extra


def parse_roadmap(text: str) -> list[Milestone]:
    """Parse phases, milestones, goals, exit criteria and (wrapped) items."""
    milestones: list[Milestone] = []
    phase = ""
    current: Milestone | None = None
    field_name: str | None = None  # the field a wrapped continuation line belongs to
    for raw in text.splitlines():
        line = raw.rstrip()
        if m := PHASE_RE.match(line):
            phase, field_name = f"Phase {m.group(1)}: {m.group(2)}", None
        elif (m := MILESTONE_RE.match(line)) or line == f"## {STRETCH}":
            current = Milestone(m.group(1), m.group(2), phase) if m else Milestone("S", STRETCH, "")
            milestones.append(current)
            field_name = None
        elif current is None or not line:
            field_name = None
        elif m := GOAL_RE.match(line):
            current.goal, field_name = m.group(1), "goal"
        elif m := EXIT_RE.match(line):
            current.exit_criteria, field_name = m.group(1), "exit"
        elif m := ITEM_RE.match(line):
            current.items.append(Item(m.group(2), int(m.group(3)), m.group(4), m.group(1) == "x"))
            field_name = "item"
        elif field_name and (line.startswith("  ") or field_name in {"goal", "exit"}):
            _continue(current, field_name, line)
        else:
            field_name = None
    return milestones


def _absolute_links(text: str, repo: str) -> str:
    """Rewrite repository-relative Markdown links so they work inside an issue."""
    base = f"https://github.com/{repo}/blob/main/"
    return re.sub(r"\]\((?!https?://|#)([^)]+)\)", lambda m: f"]({base}{m.group(1)})", text)


def issue_title(item: Item) -> str:
    """Issue title: the ID and the first clause of the item, or more if that is too short."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", item.text).replace("`", "")
    first = re.split(r"(?<=[a-z0-9)])[:;.](?:\s|$)", text, maxsplit=1)[0].strip()
    if len(first) < SHORT_CLAUSE:
        first = text.rstrip(".")
    title = f"{item.id} {first}"
    if len(title) > TITLE_MAX:
        title = title[: TITLE_MAX - 1].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return title


def item_labels(item: Item) -> list[str]:
    """Labels for an item: roadmap, size and type."""
    size = "size:S" if item.hours <= SMALL_H else "size:M" if item.hours <= MEDIUM_H else "size:L"
    labels = ["roadmap", size]
    if item.text.startswith("Spike"):
        labels.append("type:spike")
    if item.id.startswith("S"):
        labels.append("type:stretch")
    return labels


def issue_body(item: Item, milestone: Milestone, repo: str) -> str:
    """Issue body with the item, its milestone context and the hidden marker."""
    link = f"https://github.com/{repo}/blob/main/ROADMAP.md#{milestone.anchor}"
    parts = [
        _absolute_links(item.text, repo),
        "",
        f"**Estimate:** {item.hours} h · **Milestone:** [{milestone.full_title}]({link})",
    ]
    if milestone.goal:
        parts += ["", f"**Milestone goal:** {_absolute_links(milestone.goal, repo)}"]
    if milestone.exit_criteria:
        parts += ["", f"**Milestone exit criteria:** {milestone.exit_criteria}"]
    parts += [
        "",
        (
            "Done means: the definition of done in ROADMAP.md holds, the item is ticked in "
            "ROADMAP.md, and this issue is closed by the same pull request."
        ),
        "",
        MARKER.format(id=item.id),
    ]
    return "\n".join(parts)


def gh(*args: str, payload: Mapping[str, object] | None = None) -> object:
    """Call the GitHub API through ``gh api`` and return the parsed JSON."""
    cmd = ["gh", "api", *args]
    data = None
    if payload is not None:
        cmd += ["--input", "-"]
        data = json.dumps(payload)
    result = subprocess.run(cmd, input=data, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        sys.exit(f"gh api {' '.join(args)} failed: {result.stderr.strip()}")
    return json.loads(result.stdout) if result.stdout.strip() else None


def gh_paged(path: str) -> list[dict[str, object]]:
    """Fetch every page of a list endpoint."""
    pages = gh("--paginate", "--slurp", path)
    if not isinstance(pages, list):
        sys.exit(f"Unexpected response for {path}")
    return [entry for page in pages for entry in page]


@dataclass
class Syncer:
    """Applies (or prints) the changes needed to mirror the roadmap."""

    repo: str
    apply: bool
    update: bool
    milestones: dict[str, int] = field(default_factory=dict)
    issues: dict[str, dict[str, object]] = field(default_factory=dict)

    def say(self, message: str) -> None:
        """Print a planned or applied change."""
        print(("" if self.apply else "[dry run] ") + message)

    def load(self) -> None:
        """Read existing labels, milestones and roadmap issues, and create missing labels."""
        labels = {str(lab["name"]) for lab in gh_paged(f"repos/{self.repo}/labels?per_page=100")}
        for name, (color, description) in LABELS.items():
            if name not in labels:
                self.say(f"label {name}")
                if self.apply:
                    payload = {"name": name, "color": color, "description": description}
                    gh(f"repos/{self.repo}/labels", "--method", "POST", payload=payload)
        for ms in gh_paged(f"repos/{self.repo}/milestones?state=all&per_page=100"):
            self.milestones[str(ms["title"])] = int(str(ms["number"]))
        for issue in gh_paged(f"repos/{self.repo}/issues?state=all&labels=roadmap&per_page=100"):
            match = MARKER_RE.search(str(issue.get("body") or ""))
            if match and "pull_request" not in issue:
                self.issues[match.group(1)] = issue

    def ensure_milestone(self, ms: Milestone) -> int:
        """Return the number of the GitHub milestone, creating it if needed."""
        if ms.full_title not in self.milestones:
            self.say(f"milestone {ms.full_title}")
            if not self.apply:
                return 0
            payload = {"title": ms.full_title, "description": ms.goal[:1000]}
            created = gh(f"repos/{self.repo}/milestones", "--method", "POST", payload=payload)
            if not isinstance(created, dict):
                sys.exit("Milestone creation returned no data")
            self.milestones[ms.full_title] = int(created["number"])
        return self.milestones[ms.full_title]

    def sync_item(self, item: Item, ms: Milestone) -> None:
        """Create, close or update the issue of one item."""
        found = self.issues.get(item.id)
        body = issue_body(item, ms, self.repo)
        path = f"repos/{self.repo}/issues"
        if found is None and not item.done:
            self.say(f"create {issue_title(item)}")
            if self.apply:
                payload = {
                    "title": issue_title(item),
                    "body": body,
                    "labels": item_labels(item),
                    "milestone": self.ensure_milestone(ms),
                }
                gh(path, "--method", "POST", payload=payload)
                time.sleep(CREATE_DELAY_S)
        elif found is not None and item.done and found["state"] == "open":
            self.say(f"close #{found['number']} {item.id}")
            if self.apply:
                payload = {"state": "closed", "state_reason": "completed"}
                gh(f"{path}/{found['number']}", "--method", "PATCH", payload=payload)
        elif found is not None and self.update and found.get("body") != body:
            self.say(f"update #{found['number']} {item.id}")
            if self.apply:
                payload = {"title": issue_title(item), "body": body}
                gh(f"{path}/{found['number']}", "--method", "PATCH", payload=payload)


def main() -> int:
    """Parse arguments, read the roadmap and synchronise."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=DEFAULT_REPO, help="owner/name of the repository")
    parser.add_argument("--apply", action="store_true", help="make changes (default: dry run)")
    parser.add_argument("--update", action="store_true", help="refresh bodies of existing issues")
    parser.add_argument("--only", help="comma-separated milestone IDs, for example M0,M1")
    parser.add_argument("--include-stretch", action="store_true", help="also mirror S items")
    args = parser.parse_args()

    milestones = parse_roadmap(ROADMAP.read_text(encoding="utf-8"))
    if not args.include_stretch:
        milestones = [ms for ms in milestones if ms.id != "S"]
    if args.only:
        wanted = {part.strip() for part in args.only.split(",")}
        milestones = [ms for ms in milestones if ms.id in wanted]
    total = sum(item.hours for ms in milestones for item in ms.items)
    done = sum(item.hours for ms in milestones for item in ms.items if item.done)
    count = sum(len(ms.items) for ms in milestones)
    print(f"{len(milestones)} milestones, {count} items, {total} h ({done} h done)")
    syncer = Syncer(args.repo, apply=args.apply, update=args.update)
    syncer.load()
    for ms in milestones:
        if any(not item.done for item in ms.items):
            syncer.ensure_milestone(ms)
        for item in ms.items:
            syncer.sync_item(item, ms)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
