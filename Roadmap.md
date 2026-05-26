# ev_analysis — Project Plan

**Goal:** Reproducible Python pipeline + Klimadashboard-style visualization of Austrian EV share among new car registrations (Statistik Austria data).

**Project location:** `~/python-projects/ev_analysis`  
**Startup:** `cd ~/python-projects/ev_analysis && source .venv/bin/activate && code .`  
**Master data file:** `data/final/ev_registrations_monthly_clean.csv`  
**Last updated:** 2026-05-11

---

## Current Status

| Area | Status |
|---|---|
| Raw data processing (.ods → processed CSV) | ✅ Working |
| Data combination (processed → final CSV) | ✅ Working |
| Final CSV schema (7 columns) | ✅ Stable |
| Klimadashboard-style plot | 🟡 Working in notebook only (`notebooks/plot_advanced.ipynb`) |
| Validation script | 🔴 Outdated (5-column schema, needs update) |
| Plot script | 🔴 Not extracted from notebook yet |
| Automation / monthly update | ⬜ Not started |
| Bundesländer analysis | ⬜ Not started |

---

## Open Decisions (resolve before publishing)

These are blockers for any final/public claims. Do not finalize the chart until these are resolved.


### Solved Decisions

1. **Kfz vs Pkw denominator**: We only work with PKW data for the final csv and the plot. But the raw and processed files contain data from KFZ. 
2. **EV definition** — EV is only Elektro but we will work with emission free cars for the final csv and plot that means it will contain ELektro and Wasserstoff. Title needs to be changed in the plot. 
3. **Hydrogen classification** — "Wasserstoff(Brennstoffzelle)" is not part of Hybrid. But it will pe part of the emission free cars.
4. **Policy target source** — Source for policy target is found and documented.
5. **Statistik Austria data access** — Monthly 2019-2025 data has been added to the plot. The plot nopw only contains monthly observed data.
---

## Task List

### Priority 1 — Pipeline integrity (do these before anything else)

- [ ] **Update `src/validate_processed_data.py`** for 7-column schema  
  Current schema: `month, total_new_registrations, electric_new_registrations, ev_share, source_file`  
  Target schema: `month, total_new_registrations, electric_new_registrations, hybrid_new_registrations, ev_share, hybrid_share, source_file`  
  → See Claude Code handoff below

- [ ] **Extract plot code from `notebooks/plot_advanced.ipynb` → `src/plot_ev_share_klimadashboard.py`**  
  Stable, runnable script. No blinking marker. Remove ipywidgets (or keep as optional). Export PNG + SVG.  
  → See Claude Code handoff below

- [ ] **Remove blinking marker from notebook** (quick fix, do alongside extraction)

### Priority 2 — Documentation

- [ ] **Write `docs/ev_share_chart_spec.md`**  
  Contents: data file, source, schema, historical-vs-observed rule, Kfz/Pkw status, EV definition status, policy target status, colors, fonts, axis logic, labels, export sizes, known limitations.

- [ ] **Update README.md** with methodological note:  
  Pre-2026 data = historical estimate (yearly points). 2026+ = observed monthly data.

### Priority 3 — Open decisions / research

- [x] **Clarify Kfz vs Pkw denominator** — check raw files and pick one, document the choice
- [x] **Verify EV/hydrogen/hybrid definitions** against raw source columns
- [x] **Find official source for 100% EV by 2030 policy target**
- [x] **Follow up with Statistik Austria** on monthly 2019–2025 data access
- [] **Follow up with Klimadashboard** (no reply yet)

### Priority 4 — Future (do not start until Priority 1–2 are done)

- [ ] Add `period_type` column to final CSV (`annual_estimate` / `h1_estimate` / `observed_monthly`)
- [ ] Build `src/run_pipeline.py` (download → process → combine → validate → plot)
- [ ] Build `src/download_latest_data.py`
- [ ] Monthly scheduling via launchd
- [ ] Bundesländer analysis (long format, one row per month × Bundesland)

---

## Claude Code Handoff Snippets

Copy-paste these as context when opening a Claude Code session for a specific task.

---

### Handoff A — Fix validation script

```
Project: ev_analysis (~/python-projects/ev_analysis)
Task: Update src/validate_processed_data.py for current 7-column schema.

Current final CSV: data/final/ev_registrations_monthly_clean.csv
Schema: month, total_new_registrations, electric_new_registrations, hybrid_new_registrations, ev_share, hybrid_share, source_file

The script was written for an older 5-column schema. Update it to:
- Check all 7 required columns are present
- Parse month as YYYY-MM, flag bad formats
- Check for duplicate months (do not silently fix — print source_file for investigation)
- Check for missing values in required numeric columns
- Check ev_share = electric / total (within small tolerance)
- Check hybrid_share = hybrid / total where available
- Check ev_share and hybrid_share are in range 0–1
- Check chronological sorting
- Check no extra helper columns in output
- Fail loudly on structural/data errors
- Save clean output

Do not silently fix duplicate months. Print source_file for each duplicate so we can investigate.
```

---

### Handoff B — Extract plot to script

```
Project: ev_analysis (~/python-projects/ev_analysis)
Task: Move stable plot code from notebooks/plot_advanced.ipynb into src/plot_ev_share_klimadashboard.py

The notebook has a working Klimadashboard-style EV share plot. Extract it into a clean, runnable script.

Key rules:
- Pre-2026 data: plot as yearly markers only (not monthly line) — data is historical estimates
- 2026+ data: plot as observed monthly line, no markers, midpoints at ~mid-month
- Policy path: dashed line from 2021 baseline EV share to 100% at 2030-12-31. Label: "100 % Elektrofahrzeug-Anteil bis 2030". This is provisional — add a comment noting the source needs verification.
- No blinking marker — use a static label for the latest observed point
- German labels only
- Export PNG + SVG to outputs/

Style constants (Klimadashboard):
KD_BG = "#18181B"
KD_PANEL = "#27272A"
KD_GRID = "#71717B"
KD_TEXT = "#F4F4F5"
KD_MUTED = "#9F9FA9"
EV_COLOR = "#F5AF4A"

Read data from: data/final/ev_registrations_monthly_clean.csv
Car icon: data/car.png

Make it importable and runnable from the command line: python src/plot_ev_share_klimadashboard.py
```

---

### Handoff C — Write chart spec doc

```
Project: ev_analysis (~/python-projects/ev_analysis)
Task: Create docs/ev_share_chart_spec.md

This is a specification document for the EV share chart. It should cover:
- Data file used and source
- Final CSV schema
- Scientific rule: pre-2026 = historical estimates (yearly points only), 2026+ = observed monthly
- Kfz vs Pkw denominator status (UNRESOLVED — document both values for H1 2023)
- EV definition: currently "Elektro" only, hydrogen unclassified, hybrid = Benzin/Elektro + Diesel/Elektro
- Policy target: 100% EV by 2030 (provisional, source needed)
- Colors, fonts (Barlow), axis logic
- German-only labels
- Export sizes (300 dpi PNG + SVG)
- Known limitations

Write in German or English — the spec is for internal/handoff use.
```

---

## Key Technical Reference

**Final CSV schema:**
```
month (YYYY-MM)
total_new_registrations
electric_new_registrations
hybrid_new_registrations
ev_share
hybrid_share
source_file
```

**Fuel groups (current/provisional):**
```python
EV_COLUMNS     = ["Elektro"]
HYBRID_COLUMNS = ["Benzin/Elektro (hybrid)", "Diesel/Elektro (hybrid)"]
FOSSIL_COLUMNS = ["Benzin", "Diesel", "Flüssiggas", "Erdgas",
                  "Benzin/Flüssiggas (bivalent)", "Benzin/Erdgas (bivalent)",
                  "Benzin inkl.Flex-Fuel"]
# "Wasserstoff(Brennstoffzelle)" — unclassified, do not add to hybrid
```

**Austria filter in processed files:**
```python
df[df["Bundesland"] == "Österreich"]
# Fahrzeugklasse: inspect with df["Fahrzeugklasse"].unique() — may be "All" or "Gesamt"
```

**Plotting rule:**
- Pre-2026 → aggregate to yearly, plot as scatter markers
- 2026+ → observed monthly line, midpoint = ~14th of month
- Policy path → straight line from 2021 EV share to 1.0 at 2030-12-31, dashed, same color as EV line, lower opacity

**Known H1 2023 values (for cross-checking):**
- Pkw only: total = 126,690 | electric = 23,372 | EV share = 18.45%
- Kfz total: total = 183,190 | electric = 26,517 | EV share = 14.48%

**Style constants:**
```python
KD_BG = "#18181B"
KD_PANEL = "#27272A"
KD_GRID = "#71717B"
KD_TEXT = "#F4F4F5"
KD_MUTED = "#9F9FA9"
EV_COLOR = "#F5AF4A"  # mobility orange
```

---

## How to Use This File

1. **Check status table** at the top to know where things stand
2. **Pick the next task** from the priority list
3. **Copy the relevant handoff snippet** and paste it at the start of a Claude Code session (`claude` in terminal) or new chat
4. **Come back here** when done and tick off the task + update status table
