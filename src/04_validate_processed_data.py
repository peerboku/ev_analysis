import sys
from pathlib import Path

import pandas as pd

FINAL_FILE = Path("data/final/ev_registrations_monthly_clean.csv")

REQUIRED_COLUMNS = [
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

SHARE_COLUMNS = ["ev_share", "hybrid_share", "emission_free_share"]

TOLERANCE = 1e-6  # allowed rounding difference for share recalculation checks


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def ok(msg):
    print(f"  ✅  {msg}")

def fail(msg):
    print(f"  ❌  {msg}")

def indent(msg):
    print(f"       {msg}")


# ─────────────────────────────────────────────
# Individual checks
# ─────────────────────────────────────────────

def check_required_columns(df):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        fail(f"Required columns missing: {missing}")
        return False
    ok("Required columns present")
    return True


def check_month_format(df):
    parsed = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce")
    bad = df[parsed.isna()]["month"].tolist()
    if bad:
        fail(f"Invalid month format (expected YYYY-MM): {bad}")
        return False
    ok("Month format valid (YYYY-MM)")
    return True


def check_no_duplicates(df):
    dupes = df[df["month"].duplicated(keep=False)]["month"].unique().tolist()
    if dupes:
        fail(f"Duplicate months found: {dupes}")
        for m in dupes:
            sources = df[df["month"] == m]["source_file"].tolist()
            indent(f"{m} → {sources}")
        return False
    ok("No duplicate months")
    return True


def check_no_gaps(df):
    months = pd.period_range(
        start=df["month"].min(),
        end=df["month"].max(),
        freq="M"
    )
    expected = set(str(m) for m in months)
    actual   = set(df["month"].astype(str))
    missing  = sorted(expected - actual)
    if missing:
        fail(f"{len(missing)} missing month(s) in sequence: {missing}")
        return False
    ok(f"No gaps in sequence ({df['month'].min()} – {df['month'].max()}, {len(df)} months)")
    return True


def check_no_missing_values(df):
    numeric_cols = [c for c in REQUIRED_COLUMNS if c != "month" and c != "source_file"]
    missing_counts = df[numeric_cols].isna().sum()
    cols_with_missing = missing_counts[missing_counts > 0]
    if not cols_with_missing.empty:
        fail("Missing values found in numeric columns:")
        for col, count in cols_with_missing.items():
            bad_months = df[df[col].isna()]["month"].tolist()
            indent(f"{col}: {count} missing  → months: {bad_months}")
        return False
    ok("No missing values in required columns")
    return True


def check_share_ranges(df):
    out_of_range = {}
    for col in SHARE_COLUMNS:
        bad = df[(df[col] < 0) | (df[col] > 1)]["month"].tolist()
        if bad:
            out_of_range[col] = bad
    if out_of_range:
        fail("Shares outside [0, 1] range:")
        for col, months in out_of_range.items():
            indent(f"{col}: {months}")
        return False
    ok("All shares within [0, 1]")
    return True


def check_share_formula(df, share_col, numerator_col):
    recalc = df[numerator_col] / df["total_new_registrations"]
    diff = (df[share_col] - recalc).abs()
    bad = df[diff > TOLERANCE]["month"].tolist()
    if bad:
        fail(f"{share_col} does not match {numerator_col} / total at: {bad}")
        return False
    ok(f"{share_col} = {numerator_col} / total  ✓")
    return True


def check_chronological(df):
    if not df["month"].is_monotonic_increasing:
        fail("Months are not in chronological order")
        return False
    ok("Chronological order correct")
    return True


# ─────────────────────────────────────────────
# Summary table
# ─────────────────────────────────────────────

def print_summary_table(df, n=6):
    print()
    print(f"  {'month':<10} {'total':>8} {'electric':>10} {'ev%':>7} {'emission_free%':>15}")
    print(f"  {'-'*9} {'-'*8} {'-'*10} {'-'*7} {'-'*15}")
    for _, row in df.tail(n).iterrows():
        print(
            f"  {row['month']:<10} "
            f"{int(row['total_new_registrations']):>8,} "
            f"{int(row['electric_new_registrations']):>10,} "
            f"{row['ev_share']*100:>6.1f}% "
            f"{row['emission_free_share']*100:>14.1f}%"
        )
    print()


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    print()
    print("=" * 60)
    print("  VALIDATION")
    print(f"  {FINAL_FILE}")
    print("=" * 60)

    if not FINAL_FILE.exists():
        print(f"\n  ❌  File not found: {FINAL_FILE}")
        sys.exit(1)

    df = pd.read_csv(FINAL_FILE)

    print()

    results = []
    results.append(check_required_columns(df))

    # Stop here if columns are missing — remaining checks would crash
    if not results[-1]:
        print()
        print("  ⚠️  Column check failed. Fix the pipeline before re-running.")
        sys.exit(1)

    results.append(check_month_format(df))
    results.append(check_no_duplicates(df))
    results.append(check_no_gaps(df))
    results.append(check_no_missing_values(df))
    results.append(check_share_ranges(df))
    results.append(check_share_formula(df, "ev_share",            "electric_new_registrations"))
    results.append(check_share_formula(df, "emission_free_share", "emission_free_registrations"))
    results.append(check_share_formula(df, "hybrid_share",        "hybrid_new_registrations"))
    results.append(check_chronological(df))

    print()

    if not all(results):
        print("=" * 60)
        print("  ⚠️  VALIDATION FAILED — fix the issues above.")
        print("=" * 60)
        sys.exit(1)

    # ── All checks passed — show summary and ask for confirmation ──

    print("=" * 60)
    print("  ✅  ALL CHECKS PASSED")
    print("=" * 60)
    print()
    print(f"  Months: {len(df)}  ({df['month'].min()} – {df['month'].max()})")
    print()
    print(f"  Last {min(6, len(df))} months:")
    print_summary_table(df)

    print("=" * 60)
    answer = input("  Proceed with graph creation? [y/n]: ").strip().lower()
    print("=" * 60)
    print()

    if answer == "y":
        print("  Confirmed. Ready to create graph.")
        sys.exit(0)
    else:
        print("  Cancelled. Graph creation skipped.")
        sys.exit(1)


if __name__ == "__main__":
    main()
