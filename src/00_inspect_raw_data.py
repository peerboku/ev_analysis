from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")

files = sorted(RAW_DIR.glob("*.ods")) + sorted(RAW_DIR.glob("*.xlsx"))

print()
print("Spreadsheet files found:")
for i, file in enumerate(files):
    print(f"{i}: {file}")

if not files:
    raise FileNotFoundError(f"No .ods or .xlsx files found in {RAW_DIR}")
print()

while True:
    selection = input(f"Enter file index [0-{len(files) - 1}]: ").strip()
    if selection.isdigit():
        index = int(selection)
        if 0 <= index < len(files):
            file_path = files[index]
            break
    print("Invalid file selection. Please enter a valid index.")

print("Selected file:")
print(file_path)
print("Suffix:", file_path.suffix)
print()

engine = "odf" if file_path.suffix.lower() == ".ods" else "openpyxl"
excel_file = pd.ExcelFile(file_path, engine=engine)

print("Sheet names:")
for i, sheet in enumerate(excel_file.sheet_names):
    print(f"{i}: {sheet}")
print()

while True:
    selection = input(
        f"Enter sheet index [0-{len(excel_file.sheet_names) - 1}] or 'all': "
    ).strip().lower()
    if selection == "all":
        sheets_to_show = excel_file.sheet_names
        break
    if selection.isdigit():
        index = int(selection)
        if 0 <= index < len(excel_file.sheet_names):
            sheets_to_show = [excel_file.sheet_names[index]]
            break
    print("Invalid sheet selection. Please enter a valid index or 'all'.")

for sheet in sheets_to_show:
    print("\n" + "=" * 80)
    print(f"Sheet: {sheet}")
    print("=" * 80)

    df_sheet = pd.read_excel(
        file_path,
        sheet_name=sheet,
        header=None,
        engine=engine,
    )

    print("Shape:", df_sheet.shape)
    print(df_sheet.head(5))