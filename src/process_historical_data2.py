from pathlib import Path
import pandas as pd


HISTORICAL_FILE = Path("data/processed/ev_registrations_clean_2019_2025.csv")
FINAL_FILE = Path("data/final/ev_registrations_monthly_clean_test.csv")


def normalize_historical_data(df):
    df = df.copy()

    df["month"] = pd.to_datetime(df["month"], errors="raise")
    df["month"] = df["month"].dt.to_period("M").astype(str)

    df["total_new_registrations"] = pd.to_numeric(
        df["total_new_registrations"],
        errors="raise"
    )

    df["electric_new_registrations"] = pd.to_numeric(
        df["electric_new_registrations"],
        errors="raise"
    )

    df["ev_share"] = (
        df["electric_new_registrations"]
        / df["total_new_registrations"]
    )

    df["hybrid_new_registrations"] = pd.NA # empty not 0 because there is no data 
    df["hybrid_share"] = pd.NA # empty not 0 because there is no data 
    df["source_file"] = HISTORICAL_FILE.name

    df = df[
        [
            "month",
            "total_new_registrations",
            "electric_new_registrations",
            "hybrid_new_registrations",
            "ev_share",
            "hybrid_share",
            "source_file",
        ]
    ]

    return df


def main():
    historical_df = pd.read_csv(HISTORICAL_FILE)
    historical_df = normalize_historical_data(historical_df)

    if FINAL_FILE.exists():
        final_df = pd.read_csv(FINAL_FILE)

        # Remove months from final that are also present in the new historical data.
        # This allows the new historical file to overwrite those months.
        months_to_replace = historical_df["month"].unique()

        final_df = final_df[
            ~final_df["month"].isin(months_to_replace)
        ].copy()

        combined = pd.concat([final_df, historical_df], ignore_index=True)

    else:
        combined = historical_df

    # Safety check: after replacement, there should be no duplicate months.
    duplicate_months = combined[combined.duplicated("month", keep=False)]

    if not duplicate_months.empty:
        print("Duplicate months found after replacement:")
        print(duplicate_months.sort_values("month"))
        raise ValueError("Duplicate months remain. Not saving.")

    combined = combined.sort_values("month")

    FINAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(FINAL_FILE, index=False)

    print("Saved final master file:")
    print(FINAL_FILE)
    print("Shape:", combined.shape)
    print()
    print("Replaced months:")
    print(sorted(months_to_replace))
    print()
    print(combined.tail(12))


if __name__ == "__main__":
    main()