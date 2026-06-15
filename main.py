import subprocess
import sys
from pathlib import Path

SCRIPTS = Path("src")
HISTORICAL_CSV = Path("data/processed/ev_registrations_clean_2019_2025.csv")

STEPS = [
    ("Download raw data",       SCRIPTS / "01_download_data.py"),
    ("Process raw data",        SCRIPTS / "02_process_raw_data.py"),
    ("Combine processed data",  SCRIPTS / "03_combine_data.py"),
    ("Validate final data",     SCRIPTS / "04_validate_processed_data.py"),
    ("Plot chart",              SCRIPTS / "05_plot_graph.py"),
]


def run_step(label: str, script: Path) -> bool:
    print()
    print(f"{'='*60}")
    print(f"  {label}")
    print(f"  {script}")
    print(f"{'='*60}")

    result = subprocess.run([sys.executable, str(script)])

    if result.returncode != 0:
        print()
        print(f"  STOPPED: '{label}' exited with code {result.returncode}.")
        return False
    return True


def main():
    print()
    print("KFZ Dashboard — full pipeline")

    if HISTORICAL_CSV.exists():
        print(f"\n  Skipping step 00 (historical data already processed)")
    else:
        print(f"\n  Historical CSV not found — run src/00_process_historical_data.py manually first.")
        sys.exit(1)

    for label, script in STEPS:
        if not run_step(label, script):
            sys.exit(1)

    print()
    print("=" * 60)
    print("  Pipeline complete.")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
