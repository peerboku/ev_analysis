# ev_analysis

A reproducible Python pipeline for tracking the share of electric vehicles (EVs) among new car registrations in Austria — visualized in a [Klimadashboard](https://klimadashboard.at)-inspired style.

> **Note:** This README was created with the assistance of AI (Claude by Anthropic).

---

## What this project does

- **Downloads** the latest new-registration data (.ods) automatically from [Statistik Austria](https://www.statistik.at/statistiken/tourismus-und-verkehr/fahrzeuge/kfz-neuzulassungen)
- **Processes** raw files into clean monthly CSVs (by fuel type: electric, hybrid, fossil, etc.)
- **Combines** annual and monthly datasets into a single master CSV
- **Visualizes** the EV share over time as a Klimadashboard-style chart

![Klimadashboard EV share chart](outputs/klimadashboard_v.2.1.png)

---

## Data source

**Statistik Austria** — KFZ-Neuzulassungen nach Bundesland und Kraftstoffart/Energiequelle  
https://www.statistik.at/statistiken/tourismus-und-verkehr/fahrzeuge/kfz-neuzulassungen

Data covers Austrian new **passenger car (PKW)** registrations, broken down by fuel type and federal state (*Bundesland*), from 2019 onward.

---

## Methodological notes

Monthly observed data is available for the full period from 2019 onward. All data points are true monthly observations plotted at the approximate mid-month date.

**EV definition:** "Elektro" only. Hydrogen fuel-cell vehicles ("Wasserstoff/Brennstoffzelle") are tracked separately and are currently unclassified.  
**Policy target line:** Straight-line path from the 2021 EV share to 100% by 2030-12-31 (provisional — source under verification).

---

## Project structure

```
ev_analysis/
├── data/
│   ├── raw/            # Downloaded .ods files from Statistik Austria
│   ├── processed/      # Per-year cleaned CSVs
│   ├── final/          # Master CSV (ev_registrations_monthly_clean.csv)
│   └── media/          # Car icon used in the chart
├── notebooks/
│   ├── plot_klimadashboard_v.2.0.ipynb   # Main visualization notebook
│   ├── process_data.ipynb                # Data processing exploration
│   ├── process_historical_data.ipynb     # Historical data reconstruction
│   └── combine_processed_files.ipynb     # Combining processed files
├── src/
│   ├── 00_inspect_raw_data.py            # Inspect raw .ods structure
│   ├── 01_download_data.py               # Auto-download from Statistik Austria
│   ├── 02_process_raw_data.py            # Clean raw → processed CSV
│   ├── 03_combine_data.py                # Combine → final CSV
│   ├── process_historical_data.py        # Used once to process historical data set
│   └── validate_processed_data.py        # Data validation (WIP)
├── outputs/                              # Exported chart images (PNG/SVG)
├── requirements.txt
└── Roadmap.md                            # Project status and open tasks
```

---

## Final CSV schema

Master file: `data/final/ev_registrations_monthly_clean.csv`

| Column | Description |
|---|---|
| `month` | YYYY-MM |
| `total_new_registrations` | All new PKW registrations (Austria) |
| `electric_new_registrations` | "Elektro" only |
| `hybrid_new_registrations` | Benzin/Elektro + Diesel/Elektro (hybrid) |
| `ev_share` | `electric / total` (0–1) |
| `hybrid_share` | `hybrid / total` (0–1) |
| `source_file` | Originating raw file |

---

## Setup

```bash
git clone https://github.com/peerboku/ev_analysis.git
cd ev_analysis
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Running the pipeline

```bash
# 1. Download the latest raw data from Statistik Austria
python src/01_download_data.py

# 2. Process raw .ods file → cleaned CSV
python src/02_process_raw_data.py

# 3. Combine processed files → final master CSV
python src/03_combine_data.py
```

The visualization is currently in `notebooks/plot_klimadashboard_v.2.0.ipynb`. Open with JupyterLab:

```bash
jupyter lab
```

---

## Chart style

The chart uses a Klimadashboard-inspired dark theme:

| Role | Color |
|---|---|
| Background | `#18181B` |
| Panel | `#27272A` |
| Grid / muted text | `#71717B` / `#9F9FA9` |
| EV line (mobility orange) | `#F5AF4A` |
| Text | `#F4F4F5` |
| Font | Barlow |

---

## Status

| Component | Status |
|---|---|
| Download script | ✅ Working |
| Raw data processing | ✅ Working |
| Data combination | ✅ Working |
| Klimadashboard-style plot (notebook) | ✅ Working |
| Standalone plot script | 🔴 Not extracted yet |
| Validation script | 🟡 Needs update for current schema |
| Monthly automation | ⬜ Planned |
| Bundesländer analysis | ⬜ Planned |

See [Roadmap.md](Roadmap.md) for the full task list and open decisions.

---

## License

[MIT](LICENSE)

---

## Author

Peer Szczepaniak — student, Universität für Bodenkultur Wien (BOKU)

---

*README created with the assistance of AI (Claude by Anthropic).*
