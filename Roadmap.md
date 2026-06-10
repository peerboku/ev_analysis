# ev_analysis — Project Roadmap

**Goal:** Reproducible Python pipeline + Klimadashboard-style visualization of Austrian EV share among new car registrations (Statistik Austria data).

**Project location:** `~/python-projects/ev_analysis`  
**Startup:** `cd ~/python-projects/ev_analysis && source .venv/bin/activate && code .`  
**Master data file:** `data/final/ev_registrations_monthly_clean_v.2.0.csv`  
**Last updated:** 2026-06-10

---

## Current Status

| Area | Status |
|---|---|
| Raw data download script | ✅ Working (`src/01_download_data.py`) |
| Raw data processing (.ods → processed CSV) | ✅ Working (`src/02_process_raw_data.py`) |
| Data combination (processed → final CSV) | ✅ Working (`src/03_combine_data.py`) |
| Final CSV schema (8 columns) | ✅ Stable |
| Data coverage | ✅ 2019-01 to 2026-03 (86 months) |
| Klimadashboard-style plot | ✅ Working in notebook (`notebooks/plot_klimadashboard_v.2.0.ipynb`) |
| Chart PNG export | ✅ `outputs/klimadashboard_v.2.1.png` |
| Validation script | 🟡 Exists but needs update for 8-column schema |
| Standalone plot script | 🔴 Not extracted from notebook |
| Chart spec documentation | 🔴 Not written |
| Run-all pipeline script | ⬜ Not started |
| Monthly automation | ⬜ Not started |
| Bundesländer analysis | ⬜ Not started |

---

## Resolved Decisions

1. **Kfz vs Pkw denominator** — Using PKW data only for final CSV and plot. Raw/processed files contain KFZ data as-is.
2. **EV definition** — "Emission-free" = Elektro + Wasserstoff. Tracked as `emission_free_share` in the plot. "Elektro only" kept as `ev_share` for reference.
3. **Hydrogen classification** — "Wasserstoff/Brennstoffzelle" is NOT hybrid. It is counted in `emission_free_registrations`.
4. **Policy target source** — Österreichischer Mobilitätsmasterplan 2030. Document in `Sources/`.
5. **Historical data access** — Monthly data 2019–2025 obtained and processed. All data is now fully monthly.
6. **Klimadashboard contact** — Reached out, no reply yet.

---

## Task List

### Priority 1 — Pipeline integrity

- [ ] **Update `src/04_validate_processed_data.py`** for 8-column schema  
  Current schema: `month, total, electric, hybrid, emission_free, ev_share, hybrid_share, emission_free_share, source_file`  
  Checks needed: column presence, YYYY-MM format, no duplicate months, numeric ranges (shares 0–1), derived column consistency (`ev_share = electric / total`), chronological order.

- [ ] **Extract plot code from notebook → `src/05_plot_ev_share.py`**  
  Clean, runnable script. No blinking marker. German labels. Export PNG to `outputs/`.  
  Key rules: monthly line for all data, policy target dashed line, trend line optional, static label for latest point.

### Priority 2 — Documentation & presentation

- [ ] **Write `docs/chart_spec.md`** (internal spec)  
  Cover: data file, schema, EV/emission-free definitions, policy target source, colors, fonts, axis logic, export sizes, known limitations.

- [ ] **Update README** methodological note if anything changes in definitions or coverage.

### Priority 3 — Pipeline usability

- [ ] **Build `src/run_pipeline.py`**  
  One command to run: download → process → combine → validate → plot.

- [ ] **Add `period_type` column** to final CSV (`observed_monthly` for all current data — historical estimates were replaced with real monthly data).

### Priority 4 — Future (after presentation)

- [ ] Monthly scheduling via launchd
- [ ] Bundesländer analysis (long format, one row per month × Bundesland)
- [ ] Potentially hand off visualization to Klimadashboard.at

---

## Key Technical Reference

**Final CSV schema (8 columns):**
```
month (YYYY-MM)
total_new_registrations
electric_new_registrations
hybrid_new_registrations
emission_free_registrations
ev_share
hybrid_share
emission_free_share
source_file
```

**Fuel groups:**
```python
EV_COLUMNS           = ["Elektro"]
HYBRID_COLUMNS       = ["Benzin/Elektro (hybrid)", "Diesel/Elektro (hybrid)"]
EMISSION_FREE        = ["Elektro", "Wasserstoff(Brennstoffzelle)"]
FOSSIL_COLUMNS       = ["Benzin", "Diesel", "Flüssiggas", "Erdgas",
                        "Benzin/Flüssiggas (bivalent)", "Benzin/Erdgas (bivalent)",
                        "Benzin inkl.Flex-Fuel"]
```

**Austria filter:**
```python
df[df["Bundesland"] == "Österreich"]
```

**Style constants (Klimadashboard):**
```python
KD_BG    = "#18181B"
KD_PANEL = "#27272A"
KD_GRID  = "#71717B"
KD_TEXT  = "#F4F4F5"
KD_MUTED = "#9F9FA9"
EV_COLOR = "#F5AF4A"  # mobility orange
```

**Policy target:** straight line from 2021 emission-free share → 1.0 at 2030-12-31, dashed, same color as EV line at lower opacity.

---

## How to Use This File

1. Check the **Status table** to know where things stand.
2. Pick the next task from the **priority list**.
3. Come back here when done — tick off the task and update the status table.
