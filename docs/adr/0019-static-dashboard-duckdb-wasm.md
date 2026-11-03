# ADR-0019: A static dashboard on GitHub Pages with DuckDB-WASM

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

A public demo should be free to host, fast and always available. The RWS API does not allow
browser requests (no CORS), and running Helder's services publicly costs money and attention.

## Decision

- The web app is a **SvelteKit** static site with **MapLibre GL JS** maps, **Observable Plot**
  charts and **DuckDB-WASM**, which queries small Parquet snapshots in the browser.
- A scheduled **GitHub Actions** workflow runs Helder's own pipeline in "snapshot mode" for the
  watchlist (latest values, QC flags, statuses, last 7 days of hourly aggregates, alerts),
  checks the snapshot against its data contract and size budget (≤ 15 MB), and deploys it to
  GitHub Pages. No data is committed to Git.
- When pointed at a running Helder API, the same app switches to live mode.
- Accessibility (WCAG 2.2 AA), Dutch and English, and source attribution are requirements.

## Consequences

- A public, always-on demo at no cost, refreshed on a schedule (near-real-time, not live).
- Snapshot freshness is shown prominently so nobody mistakes it for live data.
