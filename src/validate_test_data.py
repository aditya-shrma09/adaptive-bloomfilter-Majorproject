
from pathlib import Path
import pandas as pd

TEST_FILE = Path("data/test/test_flows_clean.csv")


def validate_test_data():
    if not TEST_FILE.exists():
        raise FileNotFoundError(f"Test file not found: {TEST_FILE}")

    print("=" * 55)
    print("        TEST DATASET VALIDATION")
    print("=" * 55)

    # Read the dataset
    df = pd.read_csv(
        TEST_FILE,
        dtype={"Source IP": str},
        encoding="cp1252",
    )

    # Normalize column names
    df.columns = df.columns.str.strip()

    required_columns = {"Source IP", "Timestamp"}

    # 1. Check required columns
    print("\n1. COLUMN VALIDATION")
    print("-" * 30)
    print("Columns found:", list(df.columns))

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        print("FAIL: Missing columns:", sorted(missing_columns))
        return

    if set(df.columns) != required_columns:
        print("WARNING: File contains extra columns.")

    # 2. Basic statistics
    print("\n2. DATASET STATISTICS")
    print("-" * 30)
    print(f"Total records: {len(df):,}")
    print(f"File size: {TEST_FILE.stat().st_size / (1024**2):.2f} MB")

    # 3. Source IP validation
    print("\n3. SOURCE IP STATISTICS")
    print("-" * 30)

    df["Source IP"] = df["Source IP"].fillna("").str.strip()

    missing_ips = (df["Source IP"] == "").sum()
    unique_ips = df.loc[df["Source IP"] != "", "Source IP"].nunique()
    duplicate_ip_occurrences = (
        len(df) - df.loc[df["Source IP"] != "", "Source IP"].shape[0]
        if False else
        (df["Source IP"] != "").sum() - unique_ips
    )

    print(f"Unique source IPs: {unique_ips:,}")
    print(f"Missing/empty source IPs: {missing_ips:,}")
    print(f"Repeated IP occurrences: {duplicate_ip_occurrences:,}")

    # 4. Timestamp validation
    print("\n4. TIMESTAMP VALIDATION")
    print("-" * 30)

    timestamps = pd.to_datetime(df["Timestamp"], errors="coerce")
    invalid_timestamps = timestamps.isna().sum()
    valid_timestamps = timestamps.dropna()

    print(f"Invalid timestamps: {invalid_timestamps:,}")

    if not valid_timestamps.empty:
        print(f"Earliest timestamp: {valid_timestamps.min()}")
        print(f"Latest timestamp:   {valid_timestamps.max()}")

        chronological = timestamps.is_monotonic_increasing
        print(f"Chronologically sorted: {chronological}")

        if not chronological:
            print("WARNING: Records are not sorted by timestamp.")

        print(f"Distinct timestamps: {valid_timestamps.nunique():,}")
        print(
            "Distinct minutes:",
            valid_timestamps.dt.floor("min").nunique(),
        )

    # 5. Duplicate rows
    print("\n5. DUPLICATE ROW CHECK")
    print("-" * 30)

    duplicate_rows = df.duplicated(
        subset=["Source IP", "Timestamp"]
    ).sum()

    print(f"Duplicate IP + timestamp rows: {duplicate_rows:,}")

    # 6. Final status
    print("\n6. FINAL RESULT")
    print("-" * 30)

    valid_rows = (
        (df["Source IP"] != "")
        & timestamps.notna()
    ).sum()

    print(f"Rows with valid IP and timestamp: {valid_rows:,}")

    if (
        missing_columns
        or missing_ips
        or invalid_timestamps
        or not timestamps.is_monotonic_increasing
    ):
        print("RESULT: CHECK WARNINGS ABOVE")
    else:
        print("RESULT: BASIC VALIDATION PASSED")

    print("=" * 55)


if __name__ == "__main__":
    validate_test_data()
