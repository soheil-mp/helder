# Read live chloride at drinking water intakes

Chloride is the clearest real-time drinking water indicator in the Netherlands: the legal norm
for water taken in for drinking water is an annual mean of 150 mg/l, and drinking water
companies and water managers agreed to act when the daily mean at an intake exceeds 200 mg/l
([domain research §3.3](../research/01-water-quality-domain.md#33-drinking-water)).

This tutorial reads the newest values from Rijkswaterstaat with a single small request.

## Run the example

```sh
just chloride
# or, without just:
python3 examples/latest_chloride.py
```

The output lists the sensors that lie within 1.5 km of one of RIVM's 23 surface water intakes,
with their sampling depth, value, time in UTC and status:

```text
andijk                     -150 cm      141 mg/l  2026-11-03 09:40 UTC  Ongecontroleerd below 150
                         near intake: PWN, Andijk (IJsselmeer), 0.3 km
```

`Ongecontroleerd` means Rijkswaterstaat has not validated the value yet.

## What happens under the hood

1. One WFS request to the layer `locatiesmetlaatstewaarneming`, filtered with CQL to chloride
   series updated in the last hour, with only the columns needed. The unfiltered layer is more
   than 325 MB; this request is a few kilobytes.
2. The layer labels local MET times as UTC (`…Z`). The example interprets them as UTC+1 and
   converts them to real UTC ([data sources §2](../research/02-data-sources.md#rws-wfs)).
3. Each value is compared with the 150 and 200 mg/l lines. A single 10-minute value is not a
   daily or annual mean, so the comparison is only an indication; Helder computes the real
   aggregates in milestone M14.

## Try more

```sh
python3 examples/latest_chloride.py --all                    # every updated chloride series
python3 examples/latest_chloride.py --station haringvliet.4  # one station, all depths
```

Haringvliet Kier4 measures at three depths, which shows the salt wedge as a depth profile.

*Source: Rijkswaterstaat, retrieved at run time. Indicative only, not advice.*
