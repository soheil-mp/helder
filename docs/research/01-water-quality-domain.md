# Domain research: water quality in the Netherlands

*Researched and verified on 2026-11-03. Statements marked **verified** were checked against the
live services or the primary source on that date; everything else cites its source. Values
that could not be verified from a primary source are marked **to transcribe** and have a roadmap
item that copies them from the cited document, with page references, before any code uses them.*

## 1. Why a real-time view of Dutch water quality is worth building

The Netherlands sits in the delta of the Rhine, Meuse and Scheldt. The same water is used for
drinking water, agriculture, industry, shipping, nature and recreation, often within a few
kilometres. Several pressures now compete for attention:

- **Salt intrusion.** In dry summers (2018 and 2022 were recent examples) low river discharge
  lets sea water push further inland through the Rotterdam Waterway and the Haringvliet. Drinking
  water intakes on the Lek and in the south-west depend on chloride staying low.
- **Nutrients and algal blooms.** Nitrogen and phosphorus feed algae; warm, calm summers bring
  cyanobacteria (blue-green algae) to lakes and bathing sites.
- **Micropollutants and PFAS.** Pesticides, pharmaceuticals, industrial chemicals and PFAS reach
  surface water and, through it, drinking water sources. PFAS limits for drinking water became
  stricter on 12 January 2026 (§3.3).
- **Faecal contamination of bathing water** after heavy rain, when sewers overflow.
- **Accidental spills upstream,** for which the Rhine has an international warning and alarm
  plan (§3.6).

The data to watch all of this exists, but it is spread across many organisations, formats,
vocabularies, update rhythms and legal yardsticks. Real-time sensor data is published
uncontrolled ("Ongecontroleerd") and contains errors that the public viewers do not flag
(§8). No open tool combines real-time sensors, laboratory chemistry, bathing water, groundwater
and drinking water, checks each value, and judges it against the right legal norm with its source.
That is the gap Helder fills.

## 2. Who measures what

| Organisation | Waters | What is relevant here |
| :-- | :-- | :-- |
| **Rijkswaterstaat (RWS)** | National waters ("rijkswateren"): large rivers, IJsselmeer and Markermeer, estuaries, the Wadden Sea, the coast and the North Sea | 10-minute sensor networks (temperature, conductivity, chloride, oxygen, pH, turbidity, chlorophyll fluorescence) and laboratory chemistry and microbiology; published through the WaterWebservices ([data sources](02-data-sources.md#rws)) |
| **21 water boards** (waterschappen) | Regional waters: ditches, canals, small lakes, streams | Laboratory monitoring for the Water Framework Directive; published via the Waterkwaliteitsportaal of the Informatiehuis Water |
| **Provinces** | Designate bathing waters | About 700 official bathing water locations, checked about every 14 days from 1 May to 1 October by the water quality manager (dataset description, data.overheid.nl, **verified**) |
| **10 drinking water companies** | Groundwater, surface water, dune and bank filtration | Record quality data in REWAB; RIVM publishes annual averages per pumping station (**verified**, 2012–2025) |
| **RIVM** | Drinking water, bathing water, health-based guidance | Drinking water reports, the cyanobacteria protocol (2020), PFAS guidance, maps of intakes, protection zones and supply areas |
| **Informatiehuis Water (IHW)** | All | Maintains the **Aquo** standard (vocabulary and information model for water data) and the Waterkwaliteitsportaal |
| **TNO / BRO** | Groundwater | The Key Register of the Subsurface (BRO) holds groundwater monitoring wells and groundwater analysis reports (GAR) |
| **International commissions** | Rhine (ICPR/IKSR), Meuse | Warning and alarm plans and travel-time models for accidental pollution |

Most Dutch drinking water is produced from groundwater; the rest comes from surface water taken
in directly or infiltrated through dunes and river banks. RIVM's own classification of sources
distinguishes these types ([data sources](02-data-sources.md#rivm)). RIVM lists **23 surface
water intake points** used for drinking water production, run by Dunea, Evides, Oasen, PWN,
Vitens, Waterbedrijf Groningen, WML and Waternet (**verified**, RIVM WFS layer
`rivm_bronnen_onttrekkingen_opp_water_actueel`).

## 3. The legal and normative framework

Helder never invents a threshold. Every norm it evaluates comes from a registry entry that cites
its legal or scientific source, its scope and the dates it is valid ([ADR-0013](../adr/0013-norms-as-code.md)).

### 3.1 Environment and Planning Act (Omgevingswet)

Since **1 January 2024** the Omgevingswet and its decrees replace the earlier water quality
decrees. Environmental quality standards for water bodies are now *omgevingswaarden* in the
**Besluit kwaliteit leefomgeving (Bkl)**:

- **Chemical status** of Water Framework Directive (KRW) water bodies: environmental quality
  standards for priority substances (Bkl art. 2.10 with its annex), each a separate
  *omgevingswaarde*.
- **Ecological status** (Bkl art. 2.11): biological quality elements plus supporting
  physico-chemical elements (temperature, oxygen, chloride, acidity, nutrients), whose
  standards depend on the water body type and are set in the type descriptions and
  "maatlatten" (assessment scales) maintained for the KRW (**to transcribe** per type used).
- **Specific pollutants** set nationally.

The Water Framework Directive (2000/60/EC) runs in six-year cycles; the third cycle covers
**2022–2027**. Standards for priority substances follow the EQS Directive (2008/105/EC, as
amended), which distinguishes an **annual-average EQS (AA-EQS)** and a **maximum allowable
concentration (MAC-EQS)**. The Commission proposed new lists and values in October 2022
(COM(2022) 540). The registry is versioned so adopted changes can be added with their own
valid-from dates.

### 3.2 Measuring below the limit of quantification

Commission Directive **2009/90/EC** (technical specifications for chemical analysis under the
WFD) sets two rules Helder implements:

- Results below the limit of quantification (LOQ) are set to **half the LOQ** when a mean is
  calculated (art. 5(1)).
- If a calculated mean is below the LOQ, it is reported as "less than LOQ" (art. 5(2)).

RWS reports censored values with a *limit symbol* (`Waarde_Limietsymbool`, for example `<`) in
the measurement record (**verified** in the API schema), so the rule can be applied exactly.

### 3.3 Drinking water

- The **Drinkwaterwet** and **Drinkwaterbesluit** implement the recast EU Drinking Water
  Directive **(EU) 2020/2184**.
- **PFAS:** the directive sets "Sum of PFAS" (20 named substances) at **0.10 µg/l** and "PFAS
  Total" at **0.50 µg/l**, applicable from **12 January 2026**. In the Drinkwaterbesluit the sum
  of the 20 PFAS is set at 100 ng/l (bijlage III, deel B, punt 3).
- RIVM derived an **indicative drinking water guideline of 4.4 ng/l PFOA-equivalents** (2022),
  which is health-based advice, not a legal limit. Helder shows it as guidance, never as a
  legal exceedance.
- **Chloride** (Handleiding Normering chloride drinkwater (bronnen), Rijksoverheid, 2018,
  **verified** from the document text):
  - The **annual-mean norm is 150 mg/l**, both for drinking water (Drinkwaterbesluit art. 25
    with table IIIa of bijlage A) and for surface water taken in for drinking water production.
  - The parties agreed **maximum daily means**: **200 mg/l at the intake point** and **250 mg/l
    in drinking water**. The agreement is to act when the daily mean at the intake exceeds
    200 mg/l.
  - A daily value above 150 mg/l is not by itself a breach, because the legal norm is an annual
    mean, but calls for extra alertness. Above 250 mg/l in drinking water for more than 30 days,
    adverse effects are likely.

  This makes chloride the clearest real-time drinking water indicator in the Netherlands: RWS
  measures it every 10 minutes at about 68 locations (§5, **verified**).

### 3.4 Bathing water

The **Bathing Water Directive 2006/7/EC** classifies each bathing water from at least four
seasons of *E. coli* and intestinal enterococci samples:

| Water category | Parameter (cfu/100 ml) | Excellent | Good | Sufficient |
| :-- | :-- | --: | --: | --: |
| Inland | Intestinal enterococci | 200 (P95) | 400 (P95) | 330 (P90) |
| Inland | *Escherichia coli* | 500 (P95) | 1000 (P95) | 900 (P90) |
| Coastal and transitional | Intestinal enterococci | 100 (P95) | 200 (P95) | 185 (P90) |
| Coastal and transitional | *Escherichia coli* | 250 (P95) | 500 (P95) | 500 (P90) |

Annex II evaluates percentiles on the log10 scale: with μ and σ the mean and standard deviation
of the log10 counts, the 95th percentile is antilog(μ + 1.65σ) and the 90th percentile is
antilog(μ + 1.282σ). A water that misses "sufficient" is "poor". RWS reports counts per litre
(`n/l`, **verified**), so values are divided by 10 to get counts per 100 ml.

The European Environment Agency publishes the official classification of all **757 Dutch bathing
waters** for 2015–2025 (**verified**, EEA ArcGIS service), which lets Helder check its own
classification against the official one ([M11](../../ROADMAP.md#m11--bathing-water-and-cyanobacteria)).

### 3.5 Cyanobacteria (blue-green algae)

RIVM published the **Blauwalgenprotocol 2020** (RIVM report 2020-0167, 10 September 2020),
replacing the 2012 protocol. It treats all cyanobacteria as potentially toxic and lets water
managers monitor either fluorescence corrected for the fraction of potentially toxic
cyanobacteria, or biovolume converted to a cyanobacteria-associated chlorophyll-a concentration,
which is then compared with the protocol's risk levels. The thresholds and the role of scum
layers are **to transcribe** from the report (M11.6). RWS publishes observations of cyanobacteria
scum layers (`AANWZHD`/`CYANBTRDLG`) at 278 locations and microcystin concentrations at 26
(**verified** in the catalogue). Helder reports these observations and the protocol's levels; it
does not issue swimming advice, which is the job of the provinces.

### 3.6 Accidental pollution on the Rhine

After the Sandoz accident in 1986, the ICPR set up the **International Warning and Alarm Plan**
and, with the CHR, the **Rhine Alarm Model (RAM)**, which predicts where a pollution wave is
from the local discharge and represents the difference between the wave's travel time and the
mean flow velocity with a **lag coefficient**. CHR reports an accuracy of about 89 % for travel
time and 95 % for concentration after calibration with tracer tests. The ICPR is preparing a new
travel-time model, expected by 2027. Helder implements a transparent, simplified advection model
in the same spirit ([M12](../../ROADMAP.md#m12--upstream-early-warning-and-travel-time)); it is
an indication, not an operational forecast.

### 3.7 Voluntary targets for drinking water sources

The drinking water suppliers of the large European rivers publish the **European River
Memorandum (ERM, 2020)** with target values for river water used for drinking water. They are
not legal norms. Helder can show them as a separate, clearly labelled yardstick (values **to
transcribe**, M9.8).

## 4. Parameters

Aquo codes are as published by RWS (**verified** in the catalogue and in live observations on
2026-11-03).

| Parameter | Aquo (Grootheid / Parameter) | Unit | How measured | Why it matters |
| :-- | :-- | :-- | :-- | :-- |
| Water temperature | `T` | °C (`oC`) | Sensor, 10 min | Oxygen solubility, algal growth, heat stress, cooling-water discharges |
| Electrical conductivity | `GELDHD` | mS/m | Sensor, 10 min | Total dissolved ions; the basis for computed chloride and salinity |
| Chloride | `CONCTTE` / `Cl` | mg/l | Computed from conductivity and temperature at most sensor sites (method `other:F072`, "Berekende chloride concentratie – methode NDB '80-'81"), or laboratory | Salt intrusion; drinking water and agriculture |
| Salinity | `SALNTT` | dimensionless | Sensor-derived | Estuarine mixing |
| Density | `DICHTHD` | kg/m³ | Sensor-derived | Stratification |
| Dissolved oxygen | `CONCTTE` / `O2`; `VERZDGGD` / `O2` | mg/l; % saturation | Sensor or laboratory | Fish and invertebrate survival; blooms cause supersaturation by day and depletion at night |
| Acidity | `pH` | dimensionless | Sensor or laboratory | Photosynthesis raises pH during blooms |
| Turbidity | `TROEBHD` | NTU | Sensor | Suspended matter, light climate |
| Chlorophyll fluorescence | `CONCTTE` / `CHLFRFU`; `FLUORCTE` | RFU | Sensor | Algal biomass indicator (relative units, not a concentration) |
| Chlorophyll-a | `CONCTTE` / `CHLFa` | µg/l | Laboratory | Trophic state |
| Nutrients | `Ntot`, `Ptot`, `NO3`, `NH4`, `PO4` | mg/l | Laboratory | Eutrophication |
| Metals | `Cu`, `Zn`, `Ni`, `Pb`, `Cd`, `Hg` | µg/l | Laboratory | Priority and specific pollutants |
| PFOA | `CONCTTE` / `PFOA` | µg/l | Laboratory (71 locations) | PFAS exposure through drinking water sources |
| *E. coli* | `AANTPVLME` / `E_COLI` | n/l | Laboratory (336 locations) | Bathing water |
| Intestinal enterococci | `AANTPVLME` / `INTTNLETRCCN` | n/l | Laboratory (338 locations) | Bathing water |
| Cyanobacteria scum | `AANWZHD` / `CYANBTRDLG` | presence | Field observation (278 locations) | Bathing water |

## 5. Real-time sensing in practice

On 2026-11-03 the RWS catalogue listed 1,920 metadata combinations, 2,499 locations and 92,504
location–metadata links. Filtering the "latest observation" layer to series updated in the last
day and leaving out water level, discharge, flow and waves left **591 water quality series at 113
locations** (**verified**). Most measure temperature, conductivity, chloride, salinity and
density (salt monitoring around sluices, estuaries and intakes). Oxygen, pH, turbidity and
chlorophyll fluorescence are live at a handful of sites, such as Markermeer-midden, Eemshaven,
Holwerd and Sas van Gent.

Points that shape the design:

- **Series identity.** A series is the combination of location, Aquo metadata, sampling height
  (`Bemonsteringshoogte`, in cm relative to the reference plane), commissioning programme
  (`OpdrachtgevendeInstantie`) and status. Haringvliet Kier4 measures chloride at −1000, −1100
  and −1200 cm NAP at the same time, which makes the salt wedge visible as a depth profile.
- **Status.** Real-time values arrive as `Ongecontroleerd` (not yet validated) and may later be
  replaced by `Gecontroleerd` (validated) values. Helder stores both and keeps the history
  ([ADR-0009](../adr/0009-bitemporal-observations.md)).
- **Quality codes.** Each value carries a `Kwaliteitswaardecode` (`00` normal; `99` marks
  missing values). RWS publishes the code list as an Excel file.
- **Time zone.** RWS reports times with a fixed **+01:00** offset all year, also in summer
  (a June 2026 value read `2026-06-23T08:50:00.000+01:00`; **verified**). Helder converts every
  timestamp to UTC on ingestion.
- **Latency.** At 09:33 UTC the newest 10-minute values were stamped 10:10+01:00 (09:10 UTC):
  about 20–25 minutes from measurement to publication (**verified**).

## 6. Physics Helder uses

Everything is computed from equations with published sources, never learned
([ADR-0002](../adr/0002-deterministic-rule-based-processing.md)).

- **Practical salinity** from conductivity, temperature and pressure with PSS-78, implemented in
  the TEOS-10 Gibbs SeaWater toolbox (`gsw.SP_from_C`; conductivity in mS/cm, so RWS mS/m is
  divided by 100).
- **Oxygen solubility** at the measured temperature and salinity (Garcia and Gordon, 1992,
  with the Benson and Krause, 1984, coefficients), used to cross-check mg/l against % saturation
  and to detect supersaturation.
- **Chloride from conductivity:** RWS states its method (`F072`, "NDB '80-'81") but not the
  formula in the API. A spike (M8.2) finds the published relation; until then Helder only
  compares RWS's own computed chloride with conductivity for consistency, it does not recompute it.
- **Advection travel time** along a river network, with reach velocity from discharge and
  cross-section, and a lag coefficient in the RAM tradition (§3.6).

## 7. Statistics Helder uses

All are classical statistics with closed-form or exact procedures:

- Percentiles on log-transformed counts (BWD Annex II).
- Annual and daily means with the half-LOQ rule (2009/90/EC).
- Running annual means and remaining "headroom" against an annual-mean norm.
- The Mann–Kendall trend test and Sen's slope for long-term trends (Hirsch, Slack and Smith,
  1982), with the Hamed–Rao correction for serial correlation.
- Robust spread estimates (median absolute deviation) inside the QARTOD spike test.

There is no forecasting, no classification by learned models and no anomaly detection by
machine learning.

## 8. Sensor quality control

The US Integrated Ocean Observing System publishes the **QARTOD** manuals (Quality Assurance /
Quality Control of Real-Time Oceanographic Data), including manuals for dissolved oxygen
(version 2.1, August 2018) and for temperature and salinity. Each test returns one flag:
**1** pass, **2** not evaluated, **3** suspect, **4** fail, **9** missing. Tests include
gross range, climatology, spike, rate of change, flat line, attenuated signal, gap, syntax and
location. The `ioos_qc` library (version 3.0.0, Apache-2.0) implements them in Python; Helder
uses it as the reference implementation and test oracle
([ADR-0012](../adr/0012-qartod-quality-flags.md)).

Live checks and the RWS issue tracker show why this matters. Raw data contained:

- A physically impossible value: oxygen of **1036.9 mg/l** at Kralendijk (Bonaire) on
  2026-11-03 (**verified**); oxygen saturates at roughly 8–15 mg/l in natural water.
- Values that need context before anyone can call them errors: turbidity of **833 NTU** at
  Holwerd (Wadden Sea) on the same day, and a 2019 chloride value of 9,475 mg/l at −2300 cm at
  Haringvliet Kier4 next to 59–62 mg/l at −200 and −700 cm at the same time. Either could be a
  real event (a storm, a salt wedge) or a sensor fault; only cross-sensor, depth and
  climatology checks can tell, which is why Helder flags them as *suspect* rather than deleting
  them.
- Timestamps in the future (RWS issue #23) and, in the WFS layer, local MET times labelled as
  UTC (`…Z`; **verified**: values stamped `10:10:00Z` appeared at 09:33 UTC).
- Duplicate timestamps and mixed controlled and uncontrolled values (issues #22, #48, #49).
- Zero discharges at Lobith (issue #25).
- "Latest" responses that mix in series that ended decades ago (issues #29, #47; **verified**:
  a request for three locations and three quantities returned 84 series, most of them historic).
- Inconsistent descriptions of the same parameter (issues #26, #39, #40).

## 9. Scope boundaries

- Helder shows data, checks and legal yardsticks. It does **not** give health, swimming or
  drinking advice; it links to the authorities that do.
- No forecasting, no learned models and no ML libraries
  ([ADR-0002](../adr/0002-deterministic-rule-based-processing.md)).
- No personal data. Sources are environmental; organisation identifiers (such as Chamber of
  Commerce numbers of data owners in BRO) are kept only where needed for attribution
  ([ADR-0020](../adr/0020-privacy-attribution-and-source-terms.md)).

## References

- Rijkswaterstaat, *Waterdata* user notes and WaterWebservices documentation,
  <https://rijkswaterstaatdata.nl/waterdata/> (read 2026-11-03).
- Rijkswaterstaat WaterWebservices discussion forum and issue tracker,
  <https://github.com/Rijkswaterstaat/WaterWebservices> (read 2026-11-03).
- Directive 2000/60/EC (Water Framework Directive); Directive 2008/105/EC (EQS Directive);
  Commission proposal COM(2022) 540.
- Commission Directive 2009/90/EC laying down technical specifications for chemical analysis
  and monitoring of water status.
- Directive (EU) 2020/2184 on the quality of water intended for human consumption (recast).
- Directive 2006/7/EC concerning the management of bathing water quality.
- Rijksoverheid / Helpdesk Water, *Handleiding Normering chloride drinkwater (bronnen)*, 2018.
- RIVM, *Blauwalgenprotocol 2020*, report 2020-0167.
- RIVM, *PFAS in Nederlands drinkwater vergeleken met nieuwe Europese drinkwaterrichtlijn*
  and report 2022-0149 (indicative guideline of 4.4 ng/l PFOA-equivalents).
- ICPR, *Rhine Alarm Model*, <https://www.iksr.org/en/topics/pollution/international-warning-and-alarm-plan/rhine-alarm-model>;
  CHR, *Rhine Alarm Model* brochure.
- IAWR and partners, *European River Memorandum 2020*.
- U.S. IOOS, *Manual for Real-Time Quality Control of Dissolved Oxygen Observations*, v2.1,
  2018; *Manual for Real-Time Quality Control of In-situ Temperature and Salinity Data*.
- Garcia, H. E. and Gordon, L. I. (1992), Oxygen solubility in seawater: better fitting
  equations, *Limnology and Oceanography* 37(6), 1307–1312.
- Benson, B. B. and Krause, D. (1984), The concentration and isotopic fractionation of oxygen
  dissolved in freshwater and seawater in equilibrium with the atmosphere, *Limnology and
  Oceanography* 29(3), 620–632.
- IOC, SCOR and IAPSO (2010), *The international thermodynamic equation of seawater – 2010*
  (TEOS-10).
- Hirsch, R. M., Slack, J. R. and Smith, R. A. (1982), Techniques of trend analysis for monthly
  water quality data, *Water Resources Research* 18(1), 107–121.
- Hamed, K. H. and Rao, A. R. (1998), A modified Mann-Kendall trend test for autocorrelated data,
  *Journal of Hydrology* 204, 182–196.
