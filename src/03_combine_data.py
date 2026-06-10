from pathlib import Path
import pandas as pd


PROCESSED_DIR = Path("data/processed")
FINAL_FILE = Path("data/final/ev_registrations_monthly_clean.csv")

########
# Mapping/Definition
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

# Total is derived dynamically — all columns except these are fuel types
NON_FUEL_COLS = {"Bundesland", "Fahrzeugklasse", "Datum", "source_file"}

#######
# Choose Files to combine1
######

def main():
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

if __name__ == "__main__":
    main()


df = pd.read_csv(OUTPUT_FILE)


df_PKW = df[
    (df["Bundesland"] == "Österreich") &
    (df["Fahrzeugklasse"] == "Personenkraftwagen Klasse M1")
]

df_PKW["Datum"] = pd.to_datetime(df_PKW["Datum"], errors="raise")
df_PKW["month"] = df_PKW["Datum"].dt.to_period("M").astype(str)

df_PKW["total_new_registrations"] = df_PKW[ALL_COLUMNS].sum(axis=1)
df_PKW["electric_new_registrations"] = df_PKW[EV_COLUMNS].sum(axis=1)
df_PKW["hybrid_new_registrations"] = df_PKW[HYBRID_COLUMNS].sum(axis=1)
df_PKW["emission_free_registrations"] = df_PKW[EMISSION_FREE_COLUMNS].sum(axis=1)

# EV SHARE
df_PKW["ev_share"] = (
    df_PKW["electric_new_registrations"]
    / df_PKW["total_new_registrations"]
)

# EV + HYBRID SHARE
df_PKW["hybrid_share"] = (   
    df_PKW["hybrid_new_registrations"]
    / df_PKW["total_new_registrations"]
)

df_PKW["emission_free_share"] = (
    df_PKW["emission_free_registrations"]
    / df_PKW["total_new_registrations"]
)

#########
#Create Final df
#########

final_df = df_PKW.copy()

final_df["month"] = pd.to_datetime(final_df["Datum"]).dt.to_period("M").astype(str)


final_df = final_df[
    [
        "month",
        "total_new_registrations",
        "electric_new_registrations",
        "hybrid_new_registrations",
        "emission_free_registrations",
        "ev_share",
        "hybrid_share",
        "emission_free_share",
        "source_file",
    ]
]

final_df = final_df.sort_values("month")

# If the final master file already exists, add only new months.
# Existing rows stay unchanged.
if FINAL_FILE.exists():
    existing_df = pd.read_csv(FINAL_FILE)

    existing_months = set(existing_df["month"].astype(str))

    final_df = final_df[
        ~final_df["month"].astype(str).isin(existing_months)
    ].copy()

    if final_df.empty:
        print("No new months to add.")
        print("Final file was not changed.")
    else:
        updated_df = pd.concat([existing_df, final_df], ignore_index=True)
        updated_df = updated_df.sort_values("month")

        updated_df.to_csv(FINAL_FILE, index=False)

        print("Added new rows to final file:")
        print(FINAL_FILE)
        print("Rows added:", len(final_df))
        print("New shape:", updated_df.shape)
        print(updated_df.tail(12))
        print(updated_df.dtypes)

else:
    FINAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(FINAL_FILE, index=False)

    print("Created final file:")
    print(FINAL_FILE)
    print(final_df)
    print(final_df.dtypes)
