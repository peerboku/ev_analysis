from pathlib import Path
import pandas as pd


PROCESSED_DIR = Path("data/processed")
FINAL_FILE = Path("data/final/ev_registrations_monthly_clean.csv")

########
# Column definitions
########

EV_COLUMNS = [
    "Elektro",
]

EMISSION_FREE_COLUMNS = [
    "Elektro",
    "Wasserstoff (Brennstoffzelle)",
]

HYBRID_COLUMNS = [
    "Benzin/Elektro (hybrid)",
    "Diesel/Elektro (hybrid)",
]

# Total is derived dynamically — every column except these is a fuel type
NON_FUEL_COLS = {"Bundesland", "Fahrzeugklasse", "Datum", "source_file"}


def main():

    ########
    # Load and combine all processed files
    ########

    csv_files = sorted(PROCESSED_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {PROCESSED_DIR}")

    print(f"Found {len(csv_files)} files in {PROCESSED_DIR}:")
    for f in csv_files:
        print(f"  - {f.name}")
    print()

    dataframes = []
    for f in csv_files:
        df = pd.read_csv(f)
        df["source_file"] = f.name
        dataframes.append(df)

    combined = pd.concat(dataframes, ignore_index=True, sort=False)
    print(f"Combined shape: {combined.shape}")
    print()

    ########
    # Filter to Austria PKW only
    ########

    df_pkw = combined[
        (combined["Bundesland"] == "Österreich") &
        (combined["Fahrzeugklasse"] == "Personenkraftwagen Klasse M1")
    ].copy()

    df_pkw["Datum"] = pd.to_datetime(df_pkw["Datum"], errors="raise")

    # Derive fuel_cols before adding any new columns — everything that isn't
    # metadata is a fuel type at this point
    fuel_cols = [c for c in df_pkw.columns if c not in NON_FUEL_COLS]

    df_pkw["month"] = df_pkw["Datum"].dt.to_period("M").astype(str)

    ########
    # Calculate registration counts and shares
    # axis = 1 means sum across columns in our case fuel types
    # min_count=1 means that if all fuel type columns are NaN for a row, the result will be NaN instead of 0, which is more accurate for missing data
    ########

    df_pkw["total_new_registrations"]     = df_pkw[fuel_cols].sum(axis=1, min_count=1)
    df_pkw["electric_new_registrations"]  = df_pkw[EV_COLUMNS].sum(axis=1, min_count=1)
    df_pkw["hybrid_new_registrations"]    = df_pkw[HYBRID_COLUMNS].sum(axis=1, min_count=1)
    df_pkw["emission_free_registrations"] = df_pkw[EMISSION_FREE_COLUMNS].sum(axis=1, min_count=1)

    df_pkw["ev_share"]            = df_pkw["electric_new_registrations"]  / df_pkw["total_new_registrations"]
    df_pkw["hybrid_share"]        = df_pkw["hybrid_new_registrations"]    / df_pkw["total_new_registrations"]
    df_pkw["emission_free_share"] = df_pkw["emission_free_registrations"] / df_pkw["total_new_registrations"]

    ########
    # Build and save final CSV
    ########

    final_df = df_pkw[[
        "month",
        "total_new_registrations",
        "electric_new_registrations",
        "hybrid_new_registrations",
        "emission_free_registrations",
        "ev_share",
        "hybrid_share",
        "emission_free_share",
        "source_file",
    ]].sort_values("month").reset_index(drop=True)

    FINAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(FINAL_FILE, index=False)

    print(f"Saved: {FINAL_FILE}")
    print(f"Rows: {len(final_df)}  ({final_df['month'].min()} – {final_df['month'].max()})")
    print()
    print(final_df.tail(5).to_string())


if __name__ == "__main__":
    main()
