# ADR-0018: Compose for development, Kubernetes with GitOps for production-like runs

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Contributors need a one-command local platform. The project also has to show production
practice: declarative deployments, operators, policies, secrets management and progressive
rollout, without paying for a cloud.

## Decision

- **Docker Compose** with profiles (`core`, `stream`, `serve`, `obs`) for development and CI
  end-to-end tests.
- **k3d** for a local production-like cluster: Helm charts in `deploy/charts/`, an umbrella
  chart per environment, **Argo CD** app-of-apps syncing from Git, **Strimzi** for Kafka,
  **CloudNativePG** for PostgreSQL (with backups to object storage), **KEDA** scaling consumers
  on Kafka lag, **Kyverno** policies (non-root, read-only root file system, resource limits,
  signed images only), NetworkPolicies, and **SOPS with age** for secrets in Git.
- An optional cloud demo is defined in **OpenTofu** and never required for development.

## Consequences

- The same images and configuration run in Compose, k3d and a cloud cluster.
- Kubernetes adds learning and maintenance cost; it is phased in after the platform works in
  Compose (M22).
