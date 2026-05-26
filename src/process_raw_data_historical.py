from pathlib import Path
import pandas as pd

#########
# LOAD RAW DATA
########

RAW_DIR = Path("data/raw")

files = sorted([*RAW_DIR.glob("*.ods"), *RAW_DIR.glob("*.xlsx")])

print()
print("Spreadsheet files found:")
for i, file in enumerate(files):
    print(f"{i}: {file}")

if not files:
    raise FileNotFoundError(f"No .ods or .xlsx files found in {RAW_DIR}")
print()

# Selects first raw file, can be changed later
file_path = files[2]

print("Selected file:")
print(file_path)
print("Suffix:", file_path.suffix)
print()

if file_path.suffix.lower() == ".ods":
    engine = "odf"
elif file_path.suffix.lower() == ".xlsx":
    engine = "openpyxl"
else:
    raise ValueError(f"Unsupported file type: {file_path.suffix}")

excel_file = pd.ExcelFile(file_path, engine=engine)

# Selects the sheet with the table you want to work with
sheet_name = excel_file.sheet_names[11]

df = pd.read_excel(
    file_path,
    sheet_name=sheet_name,
    header=0,
    engine=engine
)

print("Selected sheet:", sheet_name)
print("Shape:", df.shape)
print()

########
# PROCESS DATA to clean csv
########


# replace obvious missing values
df = df.replace("-", pd.NA)

# identify value columns
value_cols = [
    c for c in df.columns
    if c not in ["month"]
]

# convert value columns to numeric
for col in value_cols:
    df[col] = (
        df[col]
        .astype(str)
        .str.strip()
        .replace(["-", "nan", ""], pd.NA)
    )

    df[col] = pd.to_numeric(df[col], errors="coerce")

# Convert to int where possible
for col in value_cols:
    if df[col].dropna().apply(lambda x: x == int(x)).all():
        df[col] = df[col].astype('Int64')


#####
#  CHECKPOINT
#######
print(df.head(10))
print(df.tail(10))
print()

#######
# OUTPUT
#######

PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

output_path = PROCESSED_DIR / "ev_registrations_clean_2019_2025.csv"

df.to_csv(output_path, index=False)

df_check = pd.read_csv(output_path)

print(f"Saved processed file to: {output_path}")
print("File exists:", output_path.exists())
print()

# Prüfen ob Dateipfad existiert 
#print(output_path)
#print(output_path.exists())

# Last control
#display(df_check.head()) # Spaltennamen ?
#print(df_check.shape) # Alle Zeilen/Spalten vorhanden ?
#print(df_check.dtypes) # Richtiger datatype ?