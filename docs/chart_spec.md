# Chart Spec — Emissionsfreie PKW-Neuzulassungen

Script: `src/05_plot_graph.py`  
Output: `outputs/dashboard_emissionsfreie_pkw_neuzulassungen.png`

---

## Data

| Property | Value |
|---|---|
| Input file | `data/final/ev_registrations_monthly_clean.csv` |
| Metric plotted | `emission_free_share` |
| Metric definition | `emission_free_registrations / total_new_registrations` |
| Emission-free definition | Elektro + Wasserstoff (Brennstoffzelle) |
| Vehicle scope | PKW (Personenkraftwagen Klasse M1), Austria total only |
| Coverage | 2019-01 to current (monthly) |
| Source | Statistik Austria — KFZ-Neuzulassungen nach Bundesland und Kraftstoffart |

Monthly data points are plotted at day 14 of each month (approximate mid-month).

---

## Layout

| Property | Value |
|---|---|
| Figure size | 11 × 6 inches |
| Export DPI | 300 |
| Margins | top=0.82, bottom=0.13, left=0.08, right=0.97 |

---

## Colors

| Role | Hex | Klimadashboard token |
|---|---|---|
| Background | `#18181B` | `bg-gray-900` |
| Panel | `#27272A` | `bg-gray-800` |
| Grid / axis | `#71717B` | `bg-gray-500` |
| Muted text (tick labels) | `#9F9FA9` | `bg-gray-400` |
| Primary text | `#F4F4F5` | `bg-gray-100` |
| EV line / accent | `#F5AF4A` | `bg-mobility` |

---

## Typography

Font: `sans-serif` (Barlow intended — not yet implemented, requires local font install).  
Header title: 18pt, bold, white.  
Latest-point annotation: 11pt, bold, `#F5AF4A`.  
Policy labels: 9pt, bold, `#F5AF4A` at 50% opacity.

---

## Header

Orange rounded rectangle (`#F5AF4A`) spanning figure coordinates x=0.08–0.98, y=0.82–0.97.  
Bottom corners are squared off (overlaid plain rectangle to remove bottom rounding).  
Title text: `"Emissionsfreie PKW-Neuzulassungen"`, left-aligned inside header.  
Car icon (`data/media/car_trans.png`, zoom=0.14) anchored to the right side of the header.

---

## Chart elements

**Observed line**
- Column: `emission_free_share`
- Color: `#F5AF4A`, linewidth 2.5, no markers
- Latest point: hollow circle marker (fillstyle="none", size 8)
- Latest point annotation: `"X.X% Anteil emissionsfreier PKW-Neuzulassungen im Zeitraum\nDD.MM.YYYY – DD.MM.YYYY"`, offset (12, -8) points from the point

**Policy lines** (both dashed, linewidth 2.2, `#F5AF4A` at 50% opacity)

| Line | Start | End | Baseline |
|---|---|---|---|
| AT-Ziel | 2021-01-01 | 2029-12-31 → 100% | Mean `emission_free_share` of 2020 |
| EU-Ziel | 2021-01-01 | 2034-12-31 → 100% | Mean `emission_free_share` of 2020 |

Both lines annotated at their endpoint with label offset (-50, -10) points.  
Source: Österreichischer Mobilitätsmasterplan 2030 (`Sources/Mobilitaetsmasterplan2030.pdf`).

---

## Axes

**X-axis**
- Range: first data month − 6 months → 2034-12-31
- Major ticks: every 2 years (`YearLocator(base=2)`)
- Label format: `%Y`
- Tick direction: outward, labels below axis (`pad=4`, `va="top"`)

**Y-axis**
- Ticks: 0, 20, 40, 60, 80, 100% (80% label includes "%" suffix)
- Labels: inside plot area, left-aligned, shifted up 8pt via `ScaledTranslation`
- No tick marks (length=0)

**Spines:** all hidden except bottom (color `#71717B`, alpha 0.4).  
**Grid:** horizontal only, color `#71717B`, alpha 0.35, linewidth 1.

---

## Known limitations

- Font is currently `sans-serif` system default, not Barlow. Barlow requires manual install and `rcParams` update.
- Y-axis displays ticks up to 100% but visible range is clipped at 40% — tick labels above 40% are not visible.
- Policy target end year in the annotation label says "2035" for the EU line but the line ends at 2034-12-31. These are equivalent (end of 2034 = start of 2035 target).
