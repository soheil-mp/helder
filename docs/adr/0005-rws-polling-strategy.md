# ADR-0005: Poll RWS with the WFS latest layer; backfill gaps with the API

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

RWS publishes 10-minute values about 20 minutes after measurement. The observations API answers
one location and one quantity per request, so polling about 600 series with it would mean about
86,000 requests a day. `OphalenLaatsteWaarnemingen` accepts lists, but returns the last value of
every matching series including ones that ended decades ago (84 series for a 3 × 3 request on
2026-11-03). The WFS layer `locatiesmetlaatstewaarneming` can be filtered by time and quantity:
a 25-minute window for nine quantities returned 573 series in 207 KB.

## Decision

1. **Discovery and real-time:** every 10 minutes, query the WFS layer for surface water quality
   series updated since the last watermark minus a safety margin; emit each new value.
2. **Gap repair:** when a series' sequence shows a gap (missed polls, outages), backfill that
   series with `OphalenWaarnemingen` over the gap, bounded by the download budget.
3. **Revisions:** a daily job re-reads the last 7 days of each followed series with the API to
   capture status changes (`Ongecontroleerd` to `Gecontroleerd`) and corrections.
4. **Registry:** the catalogue is refreshed daily; series activity is derived from the latest
   layer.
5. **Time:** WFS timestamps are interpreted as MET (UTC+1) despite their `Z` suffix, guarded by a
   live contract test that compares WFS and API times.
6. **Politeness:** one request at a time per endpoint, jittered schedule, `X-API-KEY` with a
   project identifier, exponential back-off with a retry budget, and a circuit breaker.

## Consequences

- About 150 small requests a day instead of tens of thousands; about 30 MB a day.
- Two code paths (WFS and API) must agree; contract tests compare them.
- If the WFS layer is unavailable, the system degrades to API polling of a reduced watchlist.
