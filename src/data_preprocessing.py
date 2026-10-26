
import re
from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "house_prices.csv"
PROCESSED_DATA_PATH = (
    PROJECT_ROOT / "data" / "processed" / "cleaned_house_prices.csv"
)


def convert_total_price(value):
    """Convert listing prices such as '42 Lac' and '1.40 Cr' to rupees."""
    if pd.isna(value):
        return None

    text = str(value).strip().lower()
    text = text.replace(",", "").replace("₹", "").replace("inr", "").strip()

    match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*(crores?|cr|lakhs?|lacs?)",
        text,
    )

    if match:
        amount = float(match.group(1))
        unit = match.group(2)

        if unit in {"cr", "crore", "crores"}:
            return amount * 10_000_000

        return amount * 100_000

    # Do not silently interpret unknown text as a valid price.
    return None


def extract_bhk(title):
    """Extract BHK count from a property title."""
    if pd.isna(title):
        return None

    match = re.search(r"\b(\d+)\s*BHK\b", str(title), re.IGNORECASE)
    return int(match.group(1)) if match else None


def convert_area(value):
    """Convert carpet area in square feet to a numeric value."""
    if pd.isna(value):
        return None

    text = str(value).strip().lower().replace(",", "")

    match = re.search(r"(\d+(?:\.\d+)?)\s*(sq\.?\s*ft|sqft|square feet)", text)

    if match:
        return float(match.group(1))

    return None


def preprocess_data():
    """Load, clean, and save the housing dataset."""
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_DATA_PATH}\n"
            "Place house_prices.csv inside data/raw/."
        )

    df = pd.read_csv(RAW_DATA_PATH)

    print("=" * 55)
    print("DWELLIQ - DATA PREPROCESSING")
    print("=" * 55)
    print(f"Original dataset shape: {df.shape}")

    required_columns = {
        "Title",
        "Amount(in rupees)",
        "location",
        "Carpet Area",
    }

    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Dataset is missing required columns: {sorted(missing_columns)}"
        )

    # Remove duplicate rows.
    df = df.drop_duplicates().copy()

    # Create the target: total property price in rupees.
    df["total_price_rupees"] = df["Amount(in rupees)"].apply(
        convert_total_price
    )

    # Extract structured property features.
    df["BHK"] = df["Title"].apply(extract_bhk)
    df["carpet_area_sqft"] = df["Carpet Area"].apply(convert_area)

    # Normalize location labels.
    df["location"] = (
        df["location"]
        .astype("string")
        .str.strip()
        .str.lower()
        .replace("", pd.NA)
    )

    # Standardize selected categorical columns.
    categorical_columns = [
        "Status",
        "Transaction",
        "Furnishing",
        "facing",
        "Ownership",
    ]

    for column in categorical_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
                .replace("", pd.NA)
            )

    # Remove rows without a usable target.
    df = df[
        df["total_price_rupees"].notna()
        & (df["total_price_rupees"] > 0)
    ].copy()

    # Remove impossible BHK values if present.
    df.loc[~df["BHK"].between(1, 20), "BHK"] = pd.NA

    # Remove columns that are entirely empty or are identifiers/raw duplicates.
    columns_to_drop = [
        "Index",
        "Amount(in rupees)",
        "Title",
        "Description",
        "Carpet Area",
        "Dimensions",
        "Plot Area",
    ]

    df = df.drop(
        columns=[c for c in columns_to_drop if c in df.columns],
        errors="ignore",
    )

    # Save cleaned data.
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)

    print(f"Cleaned dataset shape: {df.shape}")
    print(f"Rows saved: {len(df):,}")
    print(f"Missing target values: {df['total_price_rupees'].isna().sum():,}")
    print(f"Saved to: {PROCESSED_DATA_PATH}")

    print("\nTarget price summary (rupees):")
    print(df["total_price_rupees"].describe().to_string())

    return df


if __name__ == "__main__":
    preprocess_data()
