# Security policy

## Supported versions

Helder is pre-1.0. Security fixes go into the latest release and `main` only.

## Reporting a vulnerability

Please **do not open a public issue**. Report privately through GitHub's
[private vulnerability reporting](https://github.com/soheil-mp/helder/security/advisories/new).
Include what you found, how to reproduce it, and the impact you expect.

You can expect:

- an acknowledgement within 7 days;
- an assessment and a plan within 30 days;
- credit in the release notes, if you want it.

## Scope

In scope: the code in this repository, its container images and its deployment configuration
(Compose, Helm charts, policies, workflows).

Out of scope: the upstream data services Helder reads (Rijkswaterstaat, RIVM, EEA, PDOK, BRO,
PEGELONLINE, Open-Meteo). Report problems with those to their owners.

## How the project protects itself

- No secrets in Git: gitleaks in pre-commit and over the full history in CI; secret scanning
  with push protection on GitHub.
- Dependencies are locked, licence-checked and updated by Renovate; actions and images are
  pinned by digest.
- Container images are built non-root, scanned, signed and shipped with SBOMs and provenance
  (roadmap M21).
- Helder stores no personal data and has no user accounts (ADR-0020).
