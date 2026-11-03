#!/usr/bin/env bash
# Apply the repository's GitHub settings. Safe to run repeatedly.
#
# Usage: scripts/repo-settings.sh [--with-pages] [--with-ci] [owner/repo]
#   --with-pages  enable GitHub Pages built by a workflow (once the docs workflow exists, M0.10)
#   --with-ci     require the aggregate "CI passed" check on main (once CI exists, M0.8)
# Needs: the GitHub CLI (gh), authenticated with admin rights on the repository.
#
# Replaced by OpenTofu in M24.2.
set -euo pipefail

WITH_PAGES=false
WITH_CI=false
REPO="soheil-mp/helder"
for arg in "$@"; do
  case "${arg}" in
    --with-pages) WITH_PAGES=true ;;
    --with-ci) WITH_CI=true ;;
    -*) echo "Unknown option ${arg}" >&2; exit 2 ;;
    *) REPO="${arg}" ;;
  esac
done

echo "Applying settings to ${REPO}"

# --- General ------------------------------------------------------------------
# Merge commits only: squash and rebase merges would rewrite contributors' commits.
gh repo edit "${REPO}" \
  --description "Real-time water quality for the Netherlands from open data: QARTOD-checked sensor streams, norms as code, bathing, drinking and groundwater on a small-data lakehouse (Kafka, DuckLake, Dagster, dbt, SensorThings, GitOps)." \
  --enable-issues \
  --enable-wiki=false \
  --enable-projects=false \
  --enable-merge-commit \
  --enable-squash-merge=false \
  --enable-rebase-merge=false \
  --delete-branch-on-merge

# Auto-merge lets Renovate merge development-tool patch updates once CI passes.
gh api -X PATCH "repos/${REPO}" --silent -F allow_auto_merge=true

# Workflows get read-only tokens by default and may open pull requests (release-please).
gh api -X PUT "repos/${REPO}/actions/permissions/workflow" --silent \
  -f default_workflow_permissions=read -F can_approve_pull_request_reviews=true

# --- GitHub Pages: the docs and dashboard workflows deploy the site ------------------
if [[ "${WITH_PAGES}" == true ]]; then
  if gh api "repos/${REPO}/pages" --silent 2>/dev/null; then
    gh api -X PUT "repos/${REPO}/pages" --silent -f build_type=workflow
  else
    gh api -X POST "repos/${REPO}/pages" --silent -f build_type=workflow
  fi
  gh repo edit "${REPO}" --homepage "https://${REPO%%/*}.github.io/${REPO#*/}/"
fi

# --- Labels used by issue forms and Renovate ----------------------------------------
# (roadmap, size:* and type:* labels are created by scripts/sync_roadmap_issues.py)
gh label create dependencies --repo "${REPO}" --force --color "0366d6" \
  --description "Dependency updates"
gh label create data-source --repo "${REPO}" --force --color "fbca04" \
  --description "Behaviour, terms or schema of an upstream data source"
gh label create science --repo "${REPO}" --force --color "c5def5" \
  --description "Quality control, physics, statistics or norms"

# --- Topics (at most 20) ------------------------------------------------------------
gh api -X PUT "repos/${REPO}/topics" --silent \
  -f 'names[]=water-quality' -f 'names[]=netherlands' -f 'names[]=open-data' \
  -f 'names[]=environmental-monitoring' -f 'names[]=real-time' -f 'names[]=data-engineering' \
  -f 'names[]=devops' -f 'names[]=lakehouse' -f 'names[]=ducklake' -f 'names[]=duckdb' \
  -f 'names[]=kafka' -f 'names[]=dagster' -f 'names[]=dbt' -f 'names[]=data-quality' \
  -f 'names[]=data-contracts' -f 'names[]=sensorthings' -f 'names[]=qartod' \
  -f 'names[]=kubernetes' -f 'names[]=gitops' -f 'names[]=python'

# --- Security -------------------------------------------------------------------
gh api -X PATCH "repos/${REPO}" --silent \
  -f 'security_and_analysis[secret_scanning][status]=enabled' \
  -f 'security_and_analysis[secret_scanning_push_protection][status]=enabled'
gh api -X PUT "repos/${REPO}/vulnerability-alerts" --silent
# Private vulnerability reporting backs the process in SECURITY.md (M0.11).
gh api -X PUT "repos/${REPO}/private-vulnerability-reporting" --silent

# --- Rulesets for the default branch ---------------------------------------------
# apply_ruleset NAME JSON: create the ruleset, or update it in place if it exists.
apply_ruleset() {
  local name="$1" json="$2" id
  id=$(gh api "repos/${REPO}/rulesets" --jq ".[] | select(.name == \"${name}\") | .id")
  if [[ -n "${id}" ]]; then
    gh api -X PUT "repos/${REPO}/rulesets/${id}" --silent --input - <<<"${json}"
    echo "Updated ruleset ${name} (${id})"
  else
    gh api -X POST "repos/${REPO}/rulesets" --silent --input - <<<"${json}"
    echo "Created ruleset ${name}"
  fi
}

# Published history is never rewritten: no force-pushes and no deletion of main.
# Nobody can bypass this ruleset.
apply_ruleset "protect-main" '{
  "name": "protect-main",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "non_fast_forward" },
    { "type": "deletion" }
  ]
}'

# Changes reach main through pull requests that pass CI ("CI passed" aggregates every job)
# and are merged with a merge commit. Repository admins may bypass, so the sole maintainer can
# still push small documentation fixes directly.
if [[ "${WITH_CI}" == true ]]; then
  apply_ruleset "require-ci" '{
    "name": "require-ci",
    "target": "branch",
    "enforcement": "active",
    "bypass_actors": [
      { "actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always" }
    ],
    "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
    "rules": [
      {
        "type": "pull_request",
        "parameters": {
          "required_approving_review_count": 0,
          "dismiss_stale_reviews_on_push": true,
          "require_code_owner_review": false,
          "require_last_push_approval": false,
          "required_review_thread_resolution": true,
          "allowed_merge_methods": ["merge"]
        }
      },
      {
        "type": "required_status_checks",
        "parameters": {
          "strict_required_status_checks_policy": false,
          "required_status_checks": [{ "context": "CI passed", "integration_id": 15368 }]
        }
      }
    ]
  }'
fi

echo "Done."
