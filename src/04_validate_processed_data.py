from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path("data/final")

INPUT_FILE = PROJECT_ROOT / "ev_registrations_monthly_clean_v.2.0.csv"
OUTPUT_FILE = PROJECT_ROOT / "ev_registrations_monthly_clean_validate.csv"

def main():

    #######
    # Load Data
    #######

    print("Loading processed EV registration data...")
    print(f"Input file: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    print("\nBasic file overview")
    print("-------------------")
    print(f"Shape: {df.shape}")

    print("\nColumns:")
    for col in df.columns:
        print(f"- {col}")

    print("\nFirst 5 rows:")
    print(df.head())


    #########
    ## Required Columns are present? 
    #########

    required_columns = [
        "month",
        "total_new_registrations",
        "electric_new_registrations",
        "ev_share",
        "source_file",
    ]

    print("\nRequired column check")
    print("---------------------")

    missing_required_columns = [
        col for col in required_columns if col not in df.columns
    ]

    if missing_required_columns:
        print("Missing required columns:")
        for col in missing_required_columns:
            print(f"- {col}")

        raise ValueError("Required column check failed.")

    print("All required columns are present.")

    #######
    # Can Months be interpreted correctly
    #######

    print("\nMonth parsing check")
    print("-------------------")

    df["month"] = pd.to_datetime(df["month"], errors="coerce")

    invalid_months = df[df["month"].isna()]

    if not invalid_months.empty:
        print("Rows with invalid month values:")
        print(invalid_months)

        raise ValueError("Month parsing check failed.")

    print("All month values were parsed successfully.")

    print("\nMonth range:")
    print(f"Earliest month: {df['month'].min().date()}")
    print(f"Latest month:   {df['month'].max().date()}")

    ########
    # Duplicate month check
    ########
    
    print("\nDuplicate month check")
    print("---------------------")

    duplicate_month_rows = df[df["month"].duplicated(keep=False)]

    if not duplicate_month_rows.empty:
        print("Duplicate month rows found:")
        print(
            duplicate_month_rows.sort_values("month")[
                ["month", "total_new_registrations", "electric_new_registrations", "ev_share", "source_file"]
            ]
        )

        raise ValueError("Duplicate month check failed.")

    print("No duplicate months found.")

    #########
    # Missing Value Check
    #########

    print("\nMissing values check")
    print("--------------------")

    missing_values = df[required_columns].isna().sum()

    print("Missing values by required column:")
    print(missing_values)

    columns_with_missing_values = missing_values[missing_values > 0]

    if not columns_with_missing_values.empty:
        print("\nColumns with missing values:")
        print(columns_with_missing_values)

        rows_with_missing_values = df[df[required_columns].isna().any(axis=1)]

        print("\nRows with missing required values:")
        print(rows_with_missing_values[required_columns])

        raise ValueError("Missing values check failed.")

    print("No missing values found in required columns.")
    
    ########
    # Numeric columns parsed correctly
    ########

    print("\nNumeric columns check")
    print("---------------------")

    numeric_columns = [
        "total_new_registrations",
        "electric_new_registrations",
        "ev_share",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    invalid_numeric_rows = df[df[numeric_columns].isna().any(axis=1)]

    if not invalid_numeric_rows.empty:
        print("Rows with invalid numeric values:")
        print(invalid_numeric_rows[["month", *numeric_columns, "source_file"]])

        raise ValueError("Numeric columns check failed.")

    print("All numeric columns were parsed successfully.")

    print("\nNumeric column data types:")
    print(df[numeric_columns].dtypes)

    ########
    # Chronological order of Months
    ########
    
    print("\nChronological order check")
    print("-------------------------")

    is_chronological = df["month"].is_monotonic_increasing

    if is_chronological:
        print("Rows are already sorted from oldest month to newest month.")
    else:
        print("Rows are not sorted chronologically.")
        print("Sorting rows by month...")

        df = df.sort_values("month").reset_index(drop=True)

        print("Rows have been sorted from oldest month to newest month.")
    
    ##########
    # Check EV Share Formula
    ##########

    print("\nEV share formula check")
    print("----------------------")

    zero_total_rows = df[df["total_new_registrations"] == 0]

    if not zero_total_rows.empty:
        print("Rows with total_new_registrations equal to zero:")
        print(zero_total_rows[["month", "total_new_registrations", "electric_new_registrations", "ev_share", "source_file"]])

        raise ValueError("EV share formula check failed because denominator is zero.")

    df["ev_share_recalculated"] = (
        df["electric_new_registrations"] / df["total_new_registrations"]
    )

    tolerance = 0.000001

    df["ev_share_difference"] = (
        df["ev_share"] - df["ev_share_recalculated"]
    ).abs()

    incorrect_ev_share_rows = df[df["ev_share_difference"] > tolerance]

    if not incorrect_ev_share_rows.empty:
        print("Rows where ev_share does not match recalculated EV share:")
        print(
            incorrect_ev_share_rows[
                [
                    "month",
                    "total_new_registrations",
                    "electric_new_registrations",
                    "ev_share",
                    "ev_share_recalculated",
                    "ev_share_difference",
                    "source_file",
                ]
            ]
        )

        raise ValueError("EV share formula check failed.")

    print("Existing ev_share matches recalculated EV share.")


if __name__ == "__main__":
    main()