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

# The 9 fuel columns present in every sheet (in order)
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


def parse_zusammen_sheet(df):
    """
    Parse the 'Zusammen' (Austria total) sheet.

    Layout:
      row 9     : headers  → col 0 = NaN, col 1 = NaN, col 2 = 'Benzin', ...
      data rows : col 0 = year (float), col 1 = month name, col 2-10 = fuel data
    """
    header_row = df.iloc[9, 2:11].tolist()   # 9 fuel column names
    # Month names in this sheet have leading spaces — strip before matching
    df[1] = df[1].astype(str).str.strip()

    data = df[
        df[0].notna() & df[1].isin(MONTH_MAP)
    ].copy()

    data = data.iloc[:, :11]                 # keep year, month name + 9 fuel cols
    data.columns = ["year", "month_name"] + header_row

    data["Bundesland"]     = "Österreich"
    data["year"]           = data["year"].astype(int)
    data["month_number"]   = data["month_name"].map(MONTH_MAP)

    return _build_output(data)


def parse_bundesland_sheet(df, bundesland_name):
    """
    Parse an individual Bundesland sheet.

    Layout:
      row 9     : headers → col 0 = NaN, col 1 = 'Benzin', ...
      year rows : col 0 = year string ('2019', '2020', ...), data all NaN → track year
      month rows: col 0 = month name, col 1-9 = fuel data
      total rows: col 0 = 'Zusammen' → skip (annual totals)
    """
    header_row = df.iloc[9, 1:10].tolist()   # 9 fuel column names

    rows = []
    current_year = None

    for _, row in df.iloc[10:].iterrows():
        label = str(row.iloc[0]).strip()

        # Year separator row — update tracked year, no data
        if label.isdigit() and len(label) == 4:
            current_year = int(label)
            continue

        # Annual total row — skip
        if label == "Zusammen":
            continue

        # Month data row
        if label in MONTH_MAP and current_year is not None:
            fuel_values = row.iloc[1:10].tolist()
            rows.append([current_year, label] + fuel_values)

    data = pd.DataFrame(rows, columns=["year", "month_name"] + header_row)
    data["Bundesland"]   = bundesland_name
    data["month_number"] = data["month_name"].map(MONTH_MAP)

    return _build_output(data)


def _build_output(data):
    """
    Shared final steps: rename columns, build Datum, clean values, reorder.
    """
    data = data.rename(columns=COLUMN_RENAME)

    data["Datum"] = pd.to_datetime(
        data["year"].astype(str) + "-" + data["month_number"].astype(str).str.zfill(2) + "-01"
    )
    data["Datum"]         = data["Datum"].dt.strftime("%Y-%m-%d")
    data["Fahrzeugklasse"] = FAHRZEUGKLASSE

    # Replace dash placeholders with NaN and convert to numeric
    for col in FUEL_COLS:
        if col in data.columns:
            data[col] = (
                pd.to_numeric(
                    data[col].astype(str).str.strip().replace({"-": None, "nan": None, "": None}),
                    errors="coerce"
                )
            )

    return data[["Bundesland", "Fahrzeugklasse", "Datum"] + FUEL_COLS]


def main():
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"Source file not found: {SOURCE_FILE}")

    xl = pd.ExcelFile(SOURCE_FILE, engine="openpyxl")

    # Sheets to skip: intro page and pre-processed output tab
    skip_sheets = {"Neuzulassungen", "processed"}
    bundesland_sheets = [s for s in xl.sheet_names if s not in skip_sheets]

    print(f"Source: {SOURCE_FILE.name}")
    print(f"Sheets to process: {bundesland_sheets}")
    print()

    all_frames = []

    for sheet_name in bundesland_sheets:
        df_raw = pd.read_excel(SOURCE_FILE, sheet_name=sheet_name, header=None, engine="openpyxl")

        if sheet_name == "Zusammen":
            df_clean = parse_zusammen_sheet(df_raw)
            display_name = "Österreich (Zusammen)"
        else:
            df_clean = parse_bundesland_sheet(df_raw, sheet_name)
            display_name = sheet_name

        print(f"  {display_name:25s}  {len(df_clean)} rows  "
              f"({df_clean['Datum'].min()} – {df_clean['Datum'].max()})")

        all_frames.append(df_clean)

    combined = pd.concat(all_frames, ignore_index=True)
    combined = combined.sort_values(["Datum", "Bundesland"]).reset_index(drop=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_FILE, index=False)

    print()
    print(f"Saved: {OUTPUT_FILE}")
    print(f"Total rows: {len(combined)}  ({len(bundesland_sheets)} Bundesländer × 84 months)")
    print()
    print("Sample (Österreich, first 3 rows):")
    print(combined[combined["Bundesland"] == "Österreich"].head(3).to_string())


if __name__ == "__main__":
    main()
