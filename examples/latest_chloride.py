#!/usr/bin/env python3
"""Print the latest chloride readings from Rijkswaterstaat sensors near drinking water intakes.

A stand-alone illustration of the polling strategy in ADR-0005, using only the standard library:

1. Ask the RWS WFS layer ``locatiesmetlaatstewaarneming`` for chloride series that were
   updated in the last hour (a small, filtered request instead of the 300+ MB full layer).
2. Interpret the layer's time stamps as MET (UTC+1): the layer labels them ``Z`` but they are
   local wall-clock time (verified on 2026-11-03, see docs/research/02-data-sources.md).
3. Compare each value with the agreed maximum daily mean at an intake (200 mg/l) and the
   annual-mean norm (150 mg/l). A single 10-minute value is not a daily or annual mean, so
   this is an indication only; Helder computes the real aggregates in M14.

By default it shows the sensors that lie within 1.5 km (straight line) of one of RIVM's 23
surface water intakes for drinking water. The drinking water yardsticks only make sense there;
most other chloride sensors sit in brackish or salt water.

Usage:
    python3 examples/latest_chloride.py
    python3 examples/latest_chloride.py --all
    python3 examples/latest_chloride.py --station kinderdijk.lek --station haringvliet.4

Source: Rijkswaterstaat (https://rijkswaterstaatdata.nl/waterdata/), retrieved at run time.
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import sys
import urllib.parse
import urllib.request
from datetime import UTC, datetime, timedelta, timezone

WFS_URL = "https://geo.rijkswaterstaat.nl/services/ogc/hws/DDAPI20/ows"
MET = timezone(timedelta(hours=1), "MET")
ANNUAL_MEAN_NORM_MG_L = 150.0  # Drinkwaterbesluit and intake norm (annual mean)
INTAKE_DAILY_ACTION_MG_L = 200.0  # agreed maximum daily mean at the intake point
MAX_RESPONSE_BYTES = 2_000_000  # budget guard: never read more than 2 MB
# Chloride sensors within 1.5 km of a RIVM drinking water intake (computed on 2026-11-03 from
# RIVM layer rivm_bronnen_onttrekkingen_opp_water_actueel and the RWS latest layer).
NEAR_INTAKE = {
    "andijk": "PWN, Andijk (IJsselmeer), 0.3 km",
    "nieuwegein.lekkanaal": "Waternet, Nieuwegein (Lekkanaal), 0.6 km",
    "haringvliet.2": "Evides, Scheelhoek (Haringvliet), 1.2 km",
    "haringvliet.4": "Evides, Scheelhoek (Haringvliet), 1.3 km",
    "kinderdijk.lek": "Oasen, Lekkerkerk (Lek), 1.2 km",
}
COLUMNS = (
    "CODE",
    "NAAM",
    "WAARDE_LAATSTE_METING",
    "TIJDSTIP_LAATSTE_METING",
    "BEMONSTERINGSHOOGTE",
    "STATUSWAARDE",
    "OPDRACHTGEVENDE_INSTANTIE",
)


def build_query(since_met: datetime) -> str:
    """Return the WFS GetFeature URL for chloride series updated since ``since_met``."""
    # The layer stores MET wall-clock time with a 'Z' label, so compare in the same convention.
    since_label = since_met.strftime("%Y-%m-%dT%H:%M:%SZ")
    cql = (
        f"TIJDSTIP_LAATSTE_METING > '{since_label}' AND COMPARTIMENTCODE = 'OW' "
        "AND GROOTHEIDCODE = 'CONCTTE' AND PARAMETERCODE = 'Cl'"
    )
    params = {
        "SERVICE": "WFS",
        "VERSION": "1.1.0",
        "REQUEST": "GetFeature",
        "TYPENAME": "locatiesmetlaatstewaarneming",
        "outputFormat": "csv",
        "format_options": "csvseparator:semicolon",
        "propertyName": ",".join(COLUMNS),
        "CQL_FILTER": cql,
    }
    return f"{WFS_URL}?{urllib.parse.urlencode(params)}"


def fetch(url: str) -> str:
    """Download the response with a timeout and a size limit."""
    user_agent = os.environ.get("HELDER_HTTP_USER_AGENT", "helder-example/0.0")
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})  # noqa: S310 (fixed https URL)
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
        body: bytes = response.read(MAX_RESPONSE_BYTES + 1)
    if len(body) > MAX_RESPONSE_BYTES:
        sys.exit(f"Response larger than {MAX_RESPONSE_BYTES} bytes; refusing to continue.")
    return body.decode("utf-8")


def parse_met(label: str) -> datetime:
    """Parse a layer time stamp ('2026-11-03T10:10:00.000Z') as MET and return UTC."""
    local = datetime.strptime(label.rstrip("Z") + "+0100", "%Y-%m-%dT%H:%M:%S.%f%z")
    return local.astimezone(UTC)


def indication(value_mg_l: float) -> str:
    """Return a short indication against the chloride yardsticks."""
    if value_mg_l > INTAKE_DAILY_ACTION_MG_L:
        return "above 200 (intake daily-mean action level, if sustained all day)"
    if value_mg_l > ANNUAL_MEAN_NORM_MG_L:
        return "above 150 (annual-mean norm, if sustained all year)"
    return "below 150"


def main() -> int:
    """Run the example."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--station", action="append", help="RWS location code to show (repeatable)")
    parser.add_argument("--all", action="store_true", help="show every updated chloride series")
    parser.add_argument("--minutes", type=int, default=60, help="look-back window in minutes")
    args = parser.parse_args()

    now_met = datetime.now(UTC).astimezone(MET)
    url = build_query(now_met - timedelta(minutes=args.minutes))
    rows = list(csv.DictReader(io.StringIO(fetch(url)), delimiter=";"))
    if args.station:
        rows = [row for row in rows if row["CODE"] in set(args.station)]
    elif not args.all:
        rows = [row for row in rows if row["CODE"] in NEAR_INTAKE]

    print(f"{len(rows)} chloride series updated in the last {args.minutes} minutes\n")
    for row in sorted(rows, key=lambda r: (r["CODE"], int(r["BEMONSTERINGSHOOGTE"] or 0))):
        value = float(row["WAARDE_LAATSTE_METING"])
        measured = parse_met(row["TIJDSTIP_LAATSTE_METING"])
        print(
            f"{row['CODE']:<24} {int(row['BEMONSTERINGSHOOGTE'] or 0):>6} cm "
            f"{value:>8.0f} mg/l  {measured:%Y-%m-%d %H:%M} UTC  "
            f"{row['STATUSWAARDE']:<15} {indication(value)}"
        )
        if row["CODE"] in NEAR_INTAKE:
            print(f"{'':24} near intake: {NEAR_INTAKE[row['CODE']]}")
    retrieved = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    print(f"\nSource: Rijkswaterstaat, retrieved {retrieved}. Indicative only, not advice.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
