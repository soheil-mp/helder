# Apply the repository settings

Repository settings are code: `scripts/repo-settings.sh` sets them idempotently.

```sh
just repo-settings                          # general settings, labels, topics, security, protect-main
just repo-settings --with-pages             # also GitHub Pages from a workflow (after M0.10)
just repo-settings --with-pages --with-ci   # also require "CI passed" on main (after M0.8)
```

What it sets:

- Merge commits only (no squash or rebase merges), auto-merge, branch deletion on merge.
- Read-only workflow tokens by default; workflows may open pull requests (release-please).
- Labels, topics and the description.
- Secret scanning with push protection, Dependabot alerts and private vulnerability reporting.
- Ruleset `protect-main`: no force-pushes and no deletion of `main`, without bypass.
- Ruleset `require-ci` (with `--with-ci`): pull requests with the aggregate `CI passed` check;
  repository admins may bypass for small direct fixes.

It needs the GitHub CLI with admin rights. OpenTofu replaces the script in M24.2.
