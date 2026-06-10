# ev_analysis — Project Roadmap

**Goal:** Reproducible Python pipeline + Klimadashboard-style visualization of Austrian EV share among new car registrations (Statistik Austria data).

**Project location:** `~/python-projects/ev_analysis`  
**Startup:** `cd ~/python-projects/ev_analysis && source .venv/bin/activate && code .`  
**Master data file:** `data/final/ev_registrations_monthly_clean.csv`  
**Hard deadline:** 2026-06-16 (presentation + GitHub repo submission)  
**Last updated:** 2026-06-10

---

## Current Status

| Area | Status |
|---|---|
| Historical data processing (one-time) | ✅ Working (`src/00_process_historical_data.py`) |
| Raw data download script | ✅ Working (`src/01_download_data.py`) |
| Raw data processing (.ods → processed CSV) | ✅ Working (`src/02_process_raw_data.py`) |
| Data combination (processed → final CSV) | ✅ Working (`src/03_combine_data.py`) |
| Data validation + confirmation prompt | ✅ Working (`src/04_validate_processed_data.py`) |
| Final CSV schema (8 columns) | ✅ Stable |
| Data coverage | ✅ 2019-01 to 2026-05 (89 months) |
| Klimadashboard-style plot | ✅ Working in notebook |
| Chart PNG export | ✅ `outputs/klimadashboard_v.2.1.png` |
| Standalone plot script | 🔴 Not extracted from notebook |
| Chart spec documentation | 🔴 Not written |
| Repo structure / cleanup | 🟡 In progress |
| `main.py` run-all pipeline | ⬜ Not started |
| GitHub Actions automation | ⬜ Planned (post-deadline) |
| Monthly scheduling | ⬜ Planned (post-deadline) |
| Bundesländer analysis | ⬜ Planned (post-deadline) |

---

## Resolved Decisions

1. **Kfz vs Pkw denominator** — Using PKW data only for final CSV and plot. Raw/processed files contain KFZ data as-is.
2. **EV definition** — "Emission-free" = Elektro + Wasserstoff. Tracked as `emission_free_share` in the plot. "Elektro only" kept as `ev_share` for reference.
3. **Hydrogen classification** — "Wasserstoff/Brennstoffzelle" is NOT hybrid. Counted in `emission_free_registrations`.
4. **Policy target source** — Österreichischer Mobilitätsmasterplan 2030. Document in `Sources/`.
5. **Historical data access** — Monthly data 2019–2025 obtained and processed. All data is now fully monthly.
6. **Klimadashboard contact** — Reached out 2026-06-10, awaiting reply.
7. **File versioning** — Removed version suffixes (`v.2.0`, `v.2.1`) from all filenames. Use fixed names + git for versioning.
8. **Scripts-only src structure** — No `source/` module split needed at current project scope. All scripts runnable directly.

---

## Task List

### Priority 1 — Repo cleanup (do first, everything depends on it)

- [ ] **Renumber and rename all scripts** in `scripts/`
  - `00_inspect_raw_data.py` → delete
  - `01_download_data.py` → keep, rename if clearer
  - `02_process_raw_data.py` → integrate historical data processing here (skip if already processed)
  - `03_combine_data.py` → keep
  - `04_validate_processed_data.py` → keep (fix schema, see Priority 2)
  - `05_plot_ev_share.py` → extract from notebook (see Priority 2)

- [x] **Remove version suffixes from all filenames**
  - `ev_registrations_monthly_clean_v.2.0.csv` → `ev_registrations_monthly_clean.csv` ✓
  - Notebook and PNG still use version suffix — clean up in next pass

- [ ] **Reorganize folder structure**
  ```
  ev_analysis/
  ├── data/
  │   ├── raw/
  │   ├── processed/
  │   ├── final/
  │   └── outputs/        ← move chart outputs here (or keep top-level outputs/)
  ├── notebooks/          ← exploratory only; store outputs
  ├── scripts/            ← renamed from src/, all runnable
  ├── sources/            ← policy documents
  ├── outputs/            ← final PNGs
  ├── main.py
  ├── requirements.txt
  ├── README.md
  └── Roadmap.md
  ```

- [ ] **Add changelog block** to top of each script and notebook
  ```python
  # CHANGELOG
  # 2026-06-10 — initial version
  # 2026-06-XX — description of change
  ```

### Priority 2 — Pipeline integrity

- [x] **Update `src/04_validate_processed_data.py`** for 8-column schema  
  11 checks: column presence, YYYY-MM format, no duplicates, no gaps, no missing values, counts within total, shares in 0–1, formula checks, chronological order. Summary table + manual confirmation prompt.

- [ ] **Extract plot → `scripts/05_plot_ev_share.py`**  
  Clean standalone script. German labels. No blinking marker. Export PNG to `outputs/`.  
  Rules: monthly line, dashed policy target line, static label for latest point.

- [ ] **Build `main.py`**  
  Runs full pipeline: download → process → combine → validate → plot.  
  Add skip logic: don't reprocess historical data if already present.

### Priority 3 — Documentation

- [ ] **Verify Austria 2030 policy target** — confirm Mobilitätsmasterplan 2030 target line is still current; update `Sources/` if needed.

- [ ] **Write `docs/chart_spec.md`**  
  Cover: data file, schema, EV/emission-free definitions, policy target source, colors, fonts, axis logic, export sizes, known limitations.

- [ ] **Update README** — reflect new folder structure, script names, fixed filenames.

### Priority 4 — Slides (June 14–15)

See separate slide outline. Repo must be clean before starting slides.

---

## Optional — Only if repo done by June 13

- [ ] **Send Klimadashboard email** with finished repo link; ask: full code integration, PNG only, or processed data only? *(Email sent 2026-06-10, awaiting reply.)*
- [ ] **Check Klimadashboard GitHub** — if no reply, inspect their repo (with AI assistance) to assess integration complexity.
- [ ] **Subsidy effect analysis** — optional add-on to chart or separate note.
- [ ] **Bundesland graph** and/or other vehicle categories (LKW, Zweiräder).

---

## Post-Deadline / Future

- [ ] **GitHub Actions** — automated monthly download, run tests, send email on result.
- [ ] **Monthly scheduling** via launchd (macOS).
- [ ] **Bundesländer analysis** — long format, one row per month × Bundesland.
- [ ] **Klimadashboard integration** — pending their reply on preferred format.
- [ ] **Contact Johannes** re: historical data for Schwerkraftfahrzeuge, Zweiräder, Vans from Statistik Austria.
- [ ] **`period_type` column** in final CSV (`observed_monthly` for all current data).

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
EV_COLUMNS      = ["Elektro"]
HYBRID_COLUMNS  = ["Benzin/Elektro (hybrid)", "Diesel/Elektro (hybrid)"]
EMISSION_FREE   = ["Elektro", "Wasserstoff(Brennstoffzelle)"]
FOSSIL_COLUMNS  = ["Benzin", "Diesel", "Flüssiggas", "Erdgas",
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

1. Check **Current Status** table for overview.
2. Pick next open task from the priority list.
3. Tick off and update status table when done.