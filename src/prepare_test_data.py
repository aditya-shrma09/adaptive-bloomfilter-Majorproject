
from pathlib import Path
import pandas as pd

# Input and output files
INPUT_FILE = Path("data/test/test.csv")
OUTPUT_FILE = Path("data/test/test_flows_clean.csv")

REQUIRED_COLUMNS = ["Source IP", "Timestamp"]


def prepare_test_data():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    print(f"Reading: {INPUT_FILE}")

    # Read headers and remove leading/trailing spaces
    headers = pd.read_csv(
        INPUT_FILE, nrows=0, encoding="cp1252"
    ).columns

    column_map = {
        str(column).strip(): column
        for column in headers
    }

    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in column_map
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}\n"
            f"Available columns: {list(column_map.keys())}"
        )

    # Read only the required columns
    df = pd.read_csv(
        INPUT_FILE,
        usecols=[column_map[col] for col in REQUIRED_COLUMNS],
        encoding="cp1252",
        dtype={column_map["Source IP"]: str},
    )

    # Standardize column names
    df.columns = df.columns.str.strip()

    # Clean values
    df["Source IP"] = df["Source IP"].str.strip()
    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"].astype(str).str.strip(),
        errors="coerce",
    )

    # Remove invalid rows
    df = df.dropna(subset=["Timestamp"])
    df = df[df["Source IP"].notna() & (df["Source IP"] != "")]

    # Sort by full date and time
    df = df.sort_values("Timestamp").reset_index(drop=True)

    # Save the cleaned test dataset
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("\nTest dataset prepared successfully!")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Valid records: {len(df):,}")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 5 records:")
    print(df.head())


if __name__ == "__main__":
    prepare_test_data()
