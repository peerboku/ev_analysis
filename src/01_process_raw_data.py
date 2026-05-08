from pathlib import Path
import pandas as pd

#########
# LOAD RAW DATA
########

RAW_DIR = Path("data/raw")

files = list(RAW_DIR.glob("*.ods")) #looks for files 

# Checks and prints out existing files 
files = sorted(RAW_DIR.glob("*.ods"))

print()
print("ODS files found:")
for i, file in enumerate(files):
    print(f"{i}: {file}")

if not files:
    raise FileNotFoundError(f"No .ods files found in {RAW_DIR}")
print()

# Selects first raw file, can be changed later
file_path = files[1]

print("Selected file:")
print(file_path)
print("Suffix:", file_path.suffix)
print()

ods_file = pd.ExcelFile(file_path, engine="odf")

# Selects the sheet with the table you want to work with
sheet_name = ods_file.sheet_names[3] 

df = pd.read_excel(
    file_path,
    sheet_name=sheet_name,
    header=None,
    engine="odf"
)

print("Selected sheet:", sheet_name)
print("Shape:", df.shape)
print()

########
# PROCESS DATA to clean csv
########

bundeslaender = [
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

# rename first column
df = df.rename(columns={df.columns[0]: "Bezeichnung"})
df["Bezeichnung"] = df["Bezeichnung"].astype(str).str.strip()

# Rename Kraftstoff columns
fuel_cols = df.iloc[1, 1:].tolist()
df.columns = ["Bezeichnung"] + fuel_cols

# detect Bundesland rows
df["Bundesland"] = df["Bezeichnung"].where(df["Bezeichnung"].isin(bundeslaender))
df["Bundesland"] = df["Bundesland"].ffill()

# remove rows before the first Bundesland section
df = df[df["Bundesland"].notna()].copy()

# remove last row (Fußnote)
df = df.iloc[:-1].copy()

# create Fahrzeugklasse column
df["Fahrzeugklasse"] = df["Bezeichnung"]

# Bundesland section rows represent totals
df.loc[df["Bezeichnung"].isin(bundeslaender), "Fahrzeugklasse"] = "All"

# replace obvious missing values
df = df.replace("-", pd.NA)

# identify value columns
value_cols = [
    c for c in df.columns
    if c not in ["Bundesland", "Fahrzeugklasse", "Bezeichnung"]
]

# convert value columns to numeric
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


#Add one column with the date of the data
df["Datum"] = "2024-12-31"


# reorder columns
df = df[
    ["Bundesland", "Fahrzeugklasse", "Datum"] + value_cols
]    

#Clean column names, no trailing spaces
df.columns = df.columns.str.strip()

#####
#  CHECKPOINT
#######
print(df["Bundesland"].value_counts(dropna=False))
print(df["Fahrzeugklasse"].unique())
print(df.tail(10))
print()

#######
# OUTPUT
#######

PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

output_path = PROCESSED_DIR / "ev_registrations_clean_2024.csv"

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