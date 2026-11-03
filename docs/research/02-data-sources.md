# Data sources

*Every endpoint below was called on 2026-11-03 with small, bounded requests. Sizes and timings
are what those requests returned; they are the basis of the data budgets in
[ADR-0003](../adr/0003-small-data-by-design.md). Terms marked **to confirm** get a roadmap item
that records the licence text before the connector ships.*

## Summary

| ID | Source | Access | What Helder takes | Cadence | Budget per day | Terms |
| :-- | :-- | :-- | :-- | :-- | --: | :-- |
| `rws-wws` | [RWS WaterWebservices](#rws) (DD-API 2.0) | REST/JSON, POST, no auth | Catalogue; observation windows for backfill; laboratory chemistry and bathing-water microbiology | Catalogue daily; backfill on gaps | ≤ 40 MiB | Public domain mark (Waterinfo); cite RWS and retrieval date |
| `rws-wfs` | [RWS Geoservices WFS](#rws-wfs) `locatiesmetlaatstewaarneming` | WFS 1.1.0, CSV, CQL filter | Latest value of every live water quality series | Every 10 min | ≤ 35 MiB | As above |
| `rivm-geo` | [RIVM geodata WFS](#rivm) | WFS 2.0, GeoJSON | Drinking water quality per pumping station (2012–2025); intake points; supply areas; protection zones | Weekly | ≤ 10 MiB | **To confirm** per layer (NGR metadata) |
| `eea-bwd` | [EEA bathing water](#eea) | ArcGIS REST, JSON | Official classification of 757 Dutch bathing waters, 2015–2025 | After each season | < 1 MiB | EEA reuse policy, **to confirm** |
| `pdok` | [PDOK](#pdok) | OGC API Features, ATOM | Bathing water locations, water board areas, waterways network, waste water treatment plants and outfalls, BRO groundwater index | Monthly | ≤ 20 MiB | CC0 / public domain per dataset |
| `bro-gar` | [BRO groundwater analyses](#bro) | REST, IMBRO XML | Groundwater composition near drinking water abstractions | Weekly, bounded by area | ≤ 5 MiB | Public BRO data, **to confirm** wording |
| `pegelonline` | [PEGELONLINE](#pegelonline) (Germany) | REST/JSON | Rhine water level and discharge upstream of Lobith, for travel time | Every 15 min | ≤ 5 MiB | **To confirm** |
| `open-meteo` | [Open-Meteo](#open-meteo) | REST/JSON | Hourly rainfall at bathing sites and intakes | Hourly | ≤ 2 MiB | CC BY 4.0, **to confirm** |
| `wkp` | [Waterkwaliteitsportaal](#wkp) (IHW) | Web download module, CSV and GeoPackage | Regional (water board) laboratory data, KRW water bodies | Spike first | ≤ 50 MiB once | Open data, **to confirm** licence |
| `aquo` | [Aquo domain tables](#aquo) | Web API (Semantic MediaWiki) | Parameters, quantities, units, quality codes | Weekly | < 5 MiB | **To confirm** |

Not used: [zwemwater.nl](#zwemwater) (terms limit reuse), the classic RWS services (being
switched off) and any source with data about people.

<a id="rws"></a>

## 1. Rijkswaterstaat WaterWebservices (DD-API 2.0)

**Base URL:** `https://ddapi20-waterwebservices.rijkswaterstaat.nl`
**Specification:** OpenAPI 3.1 at `/webservices-api-docs` (title "WaterWebservices", build
2.67.1 on 2026-11-03); Swagger UI at `/swagger-ui/index.html`.
**Authentication:** none. An optional `X-API-KEY` header identifies the client to RWS; Helder
sends a project identifier (`HELDER_RWS_CLIENT_ID`), never a personal e-mail address.

| Endpoint (POST) | Use in Helder |
| :-- | :-- |
| `/METADATASERVICES/OphalenCatalogus` | Daily registry refresh: locations, Aquo metadata and the link table between them |
| `/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen` | Backfill one series over a period; laboratory and bathing-water history |
| `/ONLINEWAARNEMINGENSERVICES/OphalenLaatsteWaarnemingen` | Spot checks; returns the last value of *every* matching series, including ones that ended decades ago |
| `/ONLINEWAARNEMINGENSERVICES/OphalenActueleWaarnemingen` | Investigated in M4.2: returned `204 No Content` for a request that `OphalenLaatsteWaarnemingen` answered |
| `/ONLINEWAARNEMINGENSERVICES/CheckWaarnemingenAanwezig` | Cheap existence check before a backfill |

Verified behaviour:

- **Catalogue:** `{"CatalogusFilter": {"Compartimenten": true, "Grootheden": true, "Parameters": true, "Eenheden": true, "ProcesTypes": true}}`
  returned **6.6 MB in 2.7 s**: 1,920 metadata combinations, 2,499 locations and 92,504 links,
  joined by `AquoMetadata_MessageID` and `Locatie_MessageID`. Coordinates are ETRS89 latitude
  and longitude (EPSG:4258).
- **Observation request** (one location, one quantity, one period):

  ```json
  {"Locatie": {"Code": "kinderdijk.lek"},
   "AquoPlusWaarnemingMetadata": {"AquoMetadata": {
       "Compartiment": {"Code": "OW"}, "Grootheid": {"Code": "CONCTTE"},
       "Parameter": {"Code": "Cl"}, "ProcesType": "meting"}},
   "Periode": {"Begindatumtijd": "2026-11-03T07:30:00.000+00:00",
               "Einddatumtijd": "2026-11-03T09:30:00.000+00:00"}}
  ```

  returned one series of 16 ten-minute values (110–113 mg/l chloride, sensor "NKE Smart
  Conductivity + Temperature (CT) sensor", method `other:F072`, sampling height −500 cm NAP,
  programme `ZHXXREG_ZOUT`, status `Ongecontroleerd`).
- **Empty result** is `204 No Content`, not an empty list; a malformed request is `400` with a
  field-level message. Date parsing errors now return a clear message instead of `500`.
- **Limits:** at most **160,000 observations** and **100,000 series** per request (RWS user
  notes). RWS reserves the right to throttle unreasonable use.
- **Time:** every timestamp carries `+01:00`, also in summer (MET all year).
- **New location codes:** the new service uses readable, unique codes (`kinderdijk.lek`,
  `lobith.ponton`). RWS publishes an old-to-new mapping ("was-wordt-lijst") at
  <https://wrd.rwskennisbron.nl/>.
- **Transition:** the classic services (`waterwebservices.rijkswaterstaat.nl/..._DBO`) were
  scheduled for switch-off by the end of April 2026 and were unstable before that (forum
  discussion #46). Helder uses only the new service.
- **No CORS** (issue #30): browsers cannot call the API directly, so the public dashboard reads
  Helder's own snapshots ([ADR-0019](../adr/0019-static-dashboard-duckdb-wasm.md)).
- **Known data issues** are listed in the [domain research](01-water-quality-domain.md#8-sensor-quality-control)
  and drive the quality checks in M7.

**Terms.** The "Waterinfo Rijkswateren" dataset is published under the Creative Commons Public
Domain Mark (data.overheid.nl). The RWS data site asks re-users to name the source and the date
the data was retrieved. Helder adds both to every API response and export
([ADR-0020](../adr/0020-privacy-attribution-and-source-terms.md)).

<a id="rws-wfs"></a>

## 2. Rijkswaterstaat Geoservices: latest observation per series

**URL:** `https://geo.rijkswaterstaat.nl/services/ogc/hws/DDAPI20/ows`, layer
`locatiesmetlaatstewaarneming` (also `locaties`).

This WFS layer holds one row per series with its newest value. It is the cheapest way to see
everything that changed recently, so it drives real-time ingestion
([ADR-0005](../adr/0005-rws-polling-strategy.md)):

| Request | Result |
| :-- | :-- |
| Whole layer as CSV, unfiltered | **More than 325 MB** before the 120 s timeout. Never do this. |
| `GROOTHEIDCODE='GELDHD'` only | 33 MB (mostly historic series) |
| Updated in the last day, surface water, quality quantities only | **214 KB: 591 series at 113 locations** |
| Updated in the last 25 minutes, nine quality quantities | **207 KB, 573 series, 9.7 s** |

The polling query is a CQL filter on `TIJDSTIP_LAATSTE_METING`, `COMPARTIMENTCODE` and
`GROOTHEIDCODE`, with `propertyName` limiting the columns.

**Pitfall (verified):** `TIJDSTIP_LAATSTE_METING` is written with a `Z` (UTC) suffix but holds
MET (UTC+1) wall-clock time. At 09:33 UTC the layer showed values stamped `10:10:00Z`, while
the API returned the same values as `10:10:00+01:00`. Helder treats the layer's time as MET, and
a contract test compares it with the API on every run, so the day RWS fixes the label the test
fails loudly instead of shifting every value by an hour.

<a id="rivm"></a>

## 3. RIVM geodata

**URL:** `https://data.rivm.nl/geo/wfs` (809 feature types on 2026-11-03).

| Layer | Content (verified) | Size |
| :-- | :-- | :-- |
| `inspire:drinkwaterkwaliteit` | "Kwaliteit van drinkwater in Nederland 2012 – heden": **2,341** rows of annual averages per pumping station and year (2012–2025), about 45 parameters (E. coli, enterococci, chloride, nitrate, sodium, conductivity, pH, metals, bromate, trihalomethanes, pesticides total, tritium, turbidity and more); coordinates in RD New (EPSG:28992) rounded to whole kilometres | 3.0 MB as GeoJSON |
| `ank:rivm_bronnen_onttrekkingen_opp_water_actueel` | **23** surface water intake points for drinking water, with company and location name | 3 KB |
| `ank:rivm_r81_rg_voorzieningsgebiedendrinkwaterbedrijven` | Supply areas of the **10** drinking water companies | ~250 KB per two features; simplified on ingestion |
| `alo:rivm_20260430_drinkwaterbronnen_2026` | Source types (groundwater, river water filtered in dunes, and two more) as polygons | 1.9 MB for two features; simplified |
| `ank:rivm_r79_rg_grondwaterbeschermingsgebiedendrinkwater`, `ank:rivm_r82_rg_waterwingebiedendrinkwater` | Groundwater protection zones and abstraction areas | Bounded by bounding box |

Uses: the source-to-tap graph (water body → intake → pumping station → supply area), drinking
water norms checks on annual data, and the search area for groundwater analyses.

Note: `www.rivm.nl` served an incomplete TLS certificate chain to command-line clients on
2026-11-03 (report PDFs); `data.rivm.nl` was fine.

<a id="eea"></a>

## 4. European Environment Agency: bathing water classification

**URL:** `https://water.discomap.eea.europa.eu/arcgis/rest/services/BathingWater/BathingWater_Dyna_WM_2025/MapServer/3/query`
(layer "Bathing water quality (point)").

`where=countryCode='NL'` returns **757** bathing waters with identifier (for example
`NLBW15_OW102-020`), name, water category, coordinates and the official classification for
each season from 2015 to 2025 (`qualityStatus` is 2025, `qualityStatus_minus1` is 2024, and so
on). The DISCODATA SQL endpoint (`discodata.eea.europa.eu/sql`) answered scripted queries with
`403 Forbidden` from its application gateway, so Helder uses the ArcGIS service.

Use: the reference for reconciling Helder's own BWD classification
([M15](https://github.com/soheil-mp/helder/blob/main/ROADMAP.md#m15--bathing-water-and-cyanobacteria)).

<a id="pdok"></a>

## 5. PDOK (Dutch public geodata)

All through OGC API Features (`https://api.pdok.nl/<owner>/<dataset>/ogc/v1`) unless noted.

| Dataset | Collections used | Use |
| :-- | :-- | :-- |
| `provincies/zwemwater-provinciaal-rijkswateren` (ATOM: `https://service.pdok.nl/provincies/zwemwater-provinciaal-rijkswateren/atom/v1_0/index.xml`) | Designated bathing waters (INSPIRE) | Bathing water locations; CC0 on data.overheid.nl |
| `rws/richtlijn-stedelijk-afvalwater` | `rsa_rwzi`, `rsa_lozingspunten`, `rsa_agglomeraties`, `rsa_kwetsbaargebied` | Waste water treatment plants and outfalls upstream of intakes and bathing sites |
| `hwh/waterschappen-waterbeheergebieden-imwa` | Water board management areas | Which authority manages a location |
| `hwh/waterschappen-oppervlaktewateren-imwa` | Regional surface waters | Context on maps |
| `rws/vervoersnetwerken-waterwegen-netwerk` | Waterway network | River graph for travel time (M16) |
| `tno/bro-grondwatermonitoring-in-samenhang-karakteristieken` | `gm_gar`, `gm_gmw`, `gm_gmw_monitoringtube`, `gm_gmn` | Spatial index of groundwater analyses |

<a id="bro"></a>

## 6. BRO groundwater composition (GAR)

**API:** `https://publiek.broservices.nl/gm/gar/v1/` (OpenAPI 3.1 at `/openapi`, API version
2.218.0): `GET /bro-ids`, `GET /objects/{broId}`, and table endpoints. No authentication.

- The PDOK `gm_gar` collection gives each analysis report's point, sampling time and a link to
  its IMBRO XML (for example `GAR000000000001`, sampled 2003, 11.6 KB).
- The XML holds field measurements and laboratory analyses (`garcommon:analysis`, with
  parameter, value, limit symbol, reporting limit, analytical technique and quality control
  status). **Parameters are numeric codes** that map to the BRO/Aquo parameter list (mapping in
  M5.6).
- The data owner appears as a Chamber of Commerce number (an organisation, not a person).

Helder only fetches reports inside groundwater protection zones of selected pumping stations,
and only the last ten years.

<a id="pegelonline"></a>

## 7. PEGELONLINE (German Federal Waterways and Shipping Administration)

**URL:** `https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations.json?waters=RHEIN&includeTimeseries=true`
returned **36 Rhine stations**; every station had water level (`W`) and 17 had discharge
(`Q`). No water quality series were listed on the Rhine on 2026-11-03. Helder uses discharge
upstream of Lobith as the boundary condition for travel times.

<a id="open-meteo"></a>

## 8. Open-Meteo

Hourly precipitation for bathing sites and intakes (rain is a known driver of faecal
contamination after sewer overflows). No key needed for non-commercial use. Licence **to
confirm** (CC BY 4.0 attribution).

<a id="wkp"></a>

## 9. Waterkwaliteitsportaal (Informatiehuis Water)

The portal's "Download Data" module provides all data the IHW manages: surface water
measurements from 2009 as CSV in the Aquo *IM Metingen* format, selected per year and water
manager, with metadata files describing the columns; spatial data (such as KRW water bodies) as
GeoPackage. It is a web module, so a spike (M5.9) checks whether a single bounded download (one
year, one water manager, a handful of parameters) can be scripted within the terms, and records
the licence text. Until then, regional data is out of scope.

<a id="aquo"></a>

## 10. Aquo domain tables

The Aquo standard's domain tables (parameters, quantities, units, quality judgements) are
published on aquo.nl, a Semantic MediaWiki site with an API that third-party tools already use
(for example the R package `aquodom`). RWS also embeds code and description pairs in every
response, and publishes its quality codes as an Excel file
(`aquo_kwaliteitsoordeelcodes.xlsx`). M3.1 decides the authoritative sync path.

<a id="zwemwater"></a>

## 11. Excluded: zwemwater.nl

zwemwater.nl offers an Excel file of published measures (warnings and negative advice). Its
data page says the data may be used freely "for reporting during the bathing season on the
quality of bathing water". That scope does not clearly cover an open-source platform, so Helder
does not ingest it and links to zwemwater.nl for official advice instead
([ADR-0020](../adr/0020-privacy-attribution-and-source-terms.md)).

## 12. Fixtures and tests

- Tests never call live services. Connectors are tested against **recorded, trimmed responses**
  (pytest-recording cassettes) and against a **fake RWS service** that serves synthetic series
  with injected faults (gaps, duplicates, spikes, future timestamps, mislabelled time zones).
- A nightly, opt-in **live contract suite** calls each source once with the smallest valid
  request and checks the response against its schema, so upstream changes show up as one red
  check instead of silent data drift.

<a id="intake-coverage"></a>

## 13. How well are drinking water intakes covered by live sensors?

Matching RIVM's 23 surface water intakes with the RWS chloride series that were live on
2026-11-03 (straight-line distance, computed with pyproj from RD New and ETRS89 coordinates):

| Intake (company) | Nearest live chloride sensor | Distance |
| :-- | :-- | --: |
| Andijk, IJsselmeer (PWN) | `andijk` | 0.3 km |
| Nieuwegein, Lekkanaal (Waternet) | `nieuwegein.lekkanaal` | 0.6 km |
| Lekkerkerk (Oasen) | `kinderdijk.lek` | 1.2 km |
| Scheelhoek, Haringvliet (Evides) | `haringvliet.2`, `haringvliet.4` | 1.2–1.3 km |
| Ten other Oasen sites, Lek at Bergambacht (Dunea), Loosdrecht (Waternet) | `kinderdijk.lek` or `nieuwegein.lekkanaal` | 2.4–19 km |
| Brakel, Afgedamde Maas (Dunea); Gat van de Kerksloot, Amer (Evides) | none on the same water | > 20 km |
| Heel and Roosteren (WML, Meuse) | none | > 100 km |
| Engelse Werk and Weerseloseweg (Vitens), de Punt (WBG) | none | > 40 km |

Only five sensors lie within 1.5 km of an intake, and the Meuse intakes have no live chloride
sensor at all. Distance along the water, not in a straight line, decides relevance, so
M3.6 builds reviewed station-to-intake links, and the dashboard states the coverage gap
instead of hiding it. `examples/latest_chloride.py` prints the current values of the five
nearby sensors.
