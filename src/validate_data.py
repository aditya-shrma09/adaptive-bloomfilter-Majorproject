
from pathlib import Path
import pandas as pd

file = Path("data/processed/combined_flows.csv")

if not file.exists():
    raise FileNotFoundError(f"File not found: {file}")

print("File exists:", file.exists())
print("File size (MB):", round(file.stat().st_size / (1024 * 1024), 2))

required_columns = ["Source IP", "Timestamp"]

# Read a small sample.
df = pd.read_csv(
    file,
    nrows=5,
    usecols=required_columns,
    dtype={"Source IP": str},
)

print("\nFirst 5 rows:")
print(df.to_string(index=False))

print("\nColumns:")
print(df.columns.tolist())

# Validate the complete file in chunks.
total_rows = 0
missing_source_ips = 0
invalid_timestamps = 0

for chunk in pd.read_csv(
    file,
    usecols=required_columns,
    chunksize=100_000,
    dtype={"Source IP": str},
):
    total_rows += len(chunk)

    # Count missing or empty source IPs.
    source_ips = chunk["Source IP"].str.strip()
    missing_source_ips += (
        source_ips.isna() | source_ips.eq("")
    ).sum()

    # Count missing or unparseable timestamps.
    timestamps = pd.to_datetime(
        chunk["Timestamp"].astype(str).str.strip(),
        errors="coerce",
    )
    invalid_timestamps += timestamps.isna().sum()

print("\n--- Validation Results ---")
print("Total rows:", total_rows)
print("Missing/empty source IPs:", missing_source_ips)
print("Invalid timestamps:", invalid_timestamps)
print("Valid rows:", total_rows - (
    missing_source_ips + invalid_timestamps
))
