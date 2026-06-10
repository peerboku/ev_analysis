"""
One-time script: process neuzulassungen_2019_2025_monthly.xlsx into the same
column format that 02_process_raw_data.py produces.

Run once. The output file is checked into processed/ and treated as a fixed
input by 03_combine_data.py. Re-run only if the source xlsx changes.

Output: data/processed/ev_registrations_clean_2019_2025.csv
Schema: Bundesland | Fahrzeugklasse | Datum | Benzin | Diesel | Elektro |
        Erdgas | Benzin/Flüssiggas (bivalent) | Benzin/Erdgas (bivalent) |
        Benzin/Elektro (hybrid) | Diesel/Elektro (hybrid) |
        Wasserstoff (Brennstoffzelle)
"""

from pathlib import Path
import pandas as pd

SOURCE_FILE = Path("data/raw/neuzulassungen_2019_2025_monthly.xlsx")
OUTPUT_FILE = Path("data/processed/ev_registrations_clean_2019_2025.csv")

FAHRZEUGKLASSE = "Personenkraftwagen Klasse M1"

MONTH_MAP = {
    "Jänner": 1, "Februar": 2, "März": 3, "April": 4,
    "Mai": 5, "Juni": 6, "Juli": 7, "August": 8,
    "September": 9, "Oktober": 10, "November": 11, "Dezember": 12,
}

# Standardise column names to match what 02_process_raw_data.py produces
COLUMN_RENAME = {
    "Benzin/Flüssiggas": "Benzin/Flüssiggas (bivalent)",
    "Benzin/Erdgas":     "Benzin/Erdgas (bivalent)",
}

FUEL_COLS = [
    "Benzin",
    "Diesel",
    "Elektro",
    "Erdgas",
    "Benzin/Flüssiggas (bivalent)",
    "Benzin/Erdgas (bivalent)",
    "Benzin/Elektro (hybrid)",
    "Diesel/Elektro (hybrid)",
    "Wasserstoff (Brennstoffzelle)",
]


def parse_bundesland_sheet(df, bundesland_name):
    """
    Parse a single Bundesland sheet.

    Layout:
      row 9     : headers → col 0 = NaN, col 1 = 'Benzin', col 2 = 'Diesel', ...
      year rows : col 0 = year string ('2019', '2020', ...) — track year, no data
      month rows: col 0 = month name, col 1-9 = fuel data
      total rows: col 0 = 'Zusammen' — annual totals, skip
    """
    header_row = df.iloc[9, 1:10].tolist()   # 9 fuel column names

    rows = []
    current_year = None

    for _, row in df.iloc[10:].iterrows():
        label = str(row.iloc[0]).strip()

        if label.isdigit() and len(label) == 4:
            current_year = int(label)
            continue

        if label == "Zusammen":
            continue

        if label in MONTH_MAP and current_year is not None:
            rows.append([current_year, label] + row.iloc[1:10].tolist())

    data = pd.DataFrame(rows, columns=["year", "month_name"] + header_row)
    data = data.rename(columns=COLUMN_RENAME)

    data["month_number"]   = data["month_name"].map(MONTH_MAP)
    data["Datum"]          = (
        data["year"].astype(str) + "-"
        + data["month_number"].astype(str).str.zfill(2) + "-01"
    )
    data["Bundesland"]     = bundesland_name
    data["Fahrzeugklasse"] = FAHRZEUGKLASSE

    for col in FUEL_COLS:
        if col in data.columns:
            data[col] = pd.to_numeric(
                data[col].astype(str).str.strip().replace({"-": None, "nan": None, "": None}),
                errors="coerce"
            )

    return data[["Bundesland", "Fahrzeugklasse", "Datum"] + FUEL_COLS]


def main():
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"Source file not found: {SOURCE_FILE}")

    xl = pd.ExcelFile(SOURCE_FILE, engine="openpyxl")

    # Only process the individual Bundesland sheets — skip intro, summary, pre-processed tabs
    skip_sheets = {"Neuzulassungen", "Zusammen", "processed"}
    bundesland_sheets = [s for s in xl.sheet_names if s not in skip_sheets]

    print(f"Source: {SOURCE_FILE.name}")
    print(f"Processing {len(bundesland_sheets)} Bundesland sheets: {bundesland_sheets}")
    print()

    all_frames = []

    for sheet_name in bundesland_sheets:
        df_raw = pd.read_excel(SOURCE_FILE, sheet_name=sheet_name, header=None, engine="openpyxl")
        df_clean = parse_bundesland_sheet(df_raw, sheet_name)

        print(f"  {sheet_name:20s}  {len(df_clean)} rows  "
              f"({df_clean['Datum'].min()} – {df_clean['Datum'].max()})")

        all_frames.append(df_clean)

    bundeslaender_df = pd.concat(all_frames, ignore_index=True)

    # Derive Österreich total by summing all 9 Bundesländer per month
    oesterreich_df = (
        bundeslaender_df
        .groupby("Datum", as_index=False)[FUEL_COLS]
        .sum(min_count=1)           # min_count=1 keeps NaN if all values are NaN
    )
    oesterreich_df["Bundesland"]     = "Österreich"
    oesterreich_df["Fahrzeugklasse"] = FAHRZEUGKLASSE
    oesterreich_df = oesterreich_df[["Bundesland", "Fahrzeugklasse", "Datum"] + FUEL_COLS]

    print(f"  {'Österreich (summed)':20s}  {len(oesterreich_df)} rows  "
          f"({oesterreich_df['Datum'].min()} – {oesterreich_df['Datum'].max()})")

    combined = pd.concat([bundeslaender_df, oesterreich_df], ignore_index=True)
    combined = combined.sort_values(["Datum", "Bundesland"]).reset_index(drop=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_FILE, index=False)

    print()
    print(f"Saved: {OUTPUT_FILE}")
    print(f"Total rows: {len(combined)}  (10 Bundesländer × 84 months)")
    print()
    print("Sample (Österreich, first 3 rows):")
    print(combined[combined["Bundesland"] == "Österreich"].head(3).to_string())


if __name__ == "__main__":
    main()
