# Sync the roadmap to issues

`ROADMAP.md` is the source of truth; GitHub issues mirror it.

```sh
just roadmap-sync                    # dry run: print what would change
just roadmap-sync --apply            # create milestones, labels and issues; close done items
just roadmap-sync --apply --update   # also refresh bodies of existing issues
just roadmap-sync --only M1,M2       # limit to some milestones
just roadmap-sync --include-stretch  # also mirror the stretch goals
```

The script finds existing issues by a hidden marker (`<!-- roadmap-id: M4.5 -->`), so it is
safe to run repeatedly. It needs the GitHub CLI, authenticated with write access.

When you finish an item:

1. Tick it in `ROADMAP.md` (`- [x] **M4.5** ...`) in the same pull request.
2. Close the issue from the pull request (`closes #NN`), or run the sync after merging; it
   closes issues of ticked items.

`tests/scripts/test_roadmap.py` keeps the roadmap parseable: consecutive IDs, goals and exit
criteria for every milestone, and a summary table that matches the items.
