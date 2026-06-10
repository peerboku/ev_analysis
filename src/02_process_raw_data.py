from pathlib import Path
import re
import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

BUNDESLAENDER = [
    "Österreich",
    "Burgenland",
    "Kärnten",
    "Niederösterreich",
    "Oberösterreich",
    "Salzburg",
    "Steiermark",
    "Tirol",
    "Vorarlberg",
    "Wien",
]


def process_sheet(df, year, month_number):
    """
    Takes a raw sheet dataframe and returns a clean processed dataframe.
    The sheet structure from Statistik Austria looks like:
      row 0: title row (ignored)
      row 1: fuel type headers
      row 2+: data rows, grouped by Bundesland
    """
    # First column is the label column (Bundesland name or vehicle class name)
    df = df.rename(columns={df.columns[0]: "Bezeichnung"})
    df["Bezeichnung"] = df["Bezeichnung"].astype(str).str.strip()

    # Row 1 contains the fuel type column headers — use these as column names
    fuel_cols = df.iloc[1, 1:].tolist()
    df.columns = ["Bezeichnung"] + fuel_cols

    # Forward-fill Bundesland: whenever a Bundesland name appears, tag all
    # following rows with it until the next Bundesland name appears
    df["Bundesland"] = df["Bezeichnung"].where(df["Bezeichnung"].isin(BUNDESLAENDER))
    df["Bundesland"] = df["Bundesland"].ffill()

    # Drop rows before the first Bundesland section (header rows etc.)
    df = df[df["Bundesland"].notna()].copy()

    # Drop last row (Fußnote / footnote)
    df = df.iloc[:-1].copy()

    # Vehicle class: same as Bezeichnung, except for the Bundesland total rows
    df["Fahrzeugklasse"] = df["Bezeichnung"]
    df.loc[df["Bezeichnung"].isin(BUNDESLAENDER), "Fahrzeugklasse"] = "All"

    # Replace dash placeholders with proper NA
    df = df.replace("-", pd.NA)

    # All columns except the label columns are numeric value columns
    value_cols = [
        c for c in df.columns
        if c not in ["Bundesland", "Fahrzeugklasse", "Bezeichnung"]
    ]

    # Convert to numeric: Statistik Austria uses German number formatting
    # (dot as thousands separator, comma as decimal) — strip both
    for col in value_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .replace(["-", "nan", ""], pd.NA)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Datum"] = f"{year}-{month_number:02d}-01"

    df = df[["Bundesland", "Fahrzeugklasse", "Datum"] + value_cols]
    df.columns = df.columns.str.strip()

    return df


def main():
    #########
    # SELECT FILE
    ########

    # Exclude ~$ temp files created by LibreOffice/Excel when a file is open
    files = sorted(f for f in RAW_DIR.glob("*.ods") if not f.name.startswith("~$"))

    print()
    print("ODS files found:")
    for i, f in enumerate(files):
        print(f"  {i}: {f.name}")

    if not files:
        raise FileNotFoundError(f"No .ods files found in {RAW_DIR}")
    print()

    # Always pick the most recently downloaded file
    file_path = max(files, key=lambda f: f.stat().st_mtime)
    print(f"Selected file (newest): {file_path.name}")
    print()

    # Extract year from filename (e.g. "...2026.ods" → 2026)
    year_match = re.search(r"20\d{2}", file_path.stem)
    if not year_match:
        raise ValueError(f"Could not detect year in filename: {file_path.name}")
    year = int(year_match.group())

    #########
    # DETECT SHEETS
    ########

    ods_file = pd.ExcelFile(file_path, engine="odf")
    all_sheets = ods_file.sheet_names

    # Last sheet is always the period summary (e.g. "Jänner-Mai") — skip it.
    # All other sheets are months: index 0 = January, index 1 = February, etc.
    month_sheets = all_sheets[:-1]

    print(f"Sheets found: {all_sheets}")
    print(f"Summary sheet (skipped): '{all_sheets[-1]}'")
    print(f"Month sheets to process: {month_sheets}")
    print()

    #########
    # PROCESS ALL MONTH SHEETS
    ########

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for sheet_index, sheet_name in enumerate(month_sheets):
        month_number = sheet_index + 1  # index 0 = January = month 1

        print(f"--- Processing: '{sheet_name}' → {year}-{month_number:02d} ---")

        df_raw = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            header=None,
            engine="odf"
        )

        df_clean = process_sheet(df_raw, year, month_number)

        output_path = PROCESSED_DIR / f"ev_registrations_clean_{year}_{month_number:02d}.csv"
        df_clean.to_csv(output_path, index=False)

        print(f"  Saved: {output_path.name}  ({len(df_clean)} rows)")

    print()
    print(f"Done. Processed {len(month_sheets)} month(s) from {file_path.name}")
    print()

if __name__ == "__main__":
    main()
