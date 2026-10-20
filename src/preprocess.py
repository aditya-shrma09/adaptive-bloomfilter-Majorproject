
from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "combined_flows.csv"

REQUIRED_COLUMNS = [
    "Source IP",
    "Timestamp",
]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

csv_files = sorted(RAW_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {RAW_DIR}")

# Start with a fresh output on every run.
if OUTPUT_FILE.exists():
    OUTPUT_FILE.unlink()

first_chunk = True

for file in csv_files:
    print(f"Processing: {file.name}")

    # Read headers and normalize whitespace.
    headers = pd.read_csv(
        file,
        nrows=0,
        encoding="cp1252",
    ).columns

    actual_names = {
        str(col).strip(): col for col in headers
    }

    missing = set(REQUIRED_COLUMNS) - set(actual_names)

    if missing:
        print(
            f"Skipping {file.name}; "
            f"missing columns: {sorted(missing)}"
        )
        continue

    usecols = [
        actual_names[col] for col in REQUIRED_COLUMNS
    ]

    for chunk in pd.read_csv(
        file,
        usecols=usecols,
        chunksize=100_000,
        encoding="cp1252",
        dtype={actual_names["Source IP"]: str},
    ):
        # Standardize column names.
        chunk.columns = chunk.columns.str.strip()

        # Clean source IP and parse timestamps.
        chunk["Source IP"] = chunk["Source IP"].str.strip()

        chunk["Timestamp"] = pd.to_datetime(
            chunk["Timestamp"].astype(str).str.strip(),
            errors="coerce",
        )

        # Remove rows without a usable IP or timestamp.
        chunk = chunk.dropna(
            subset=["Source IP", "Timestamp"]
        )
        chunk = chunk[chunk["Source IP"] != ""]

        if chunk.empty:
            continue

        chunk.to_csv(
            OUTPUT_FILE,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False,
        )
        first_chunk = False

if first_chunk:
    print("No valid rows were written. Check the CSV files.")
else:
    print(f"Finished! Output saved to {OUTPUT_FILE}")
