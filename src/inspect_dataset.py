
import pandas as pd
from pathlib import Path

# Dataset location
PROJECT_ROOT = Path(__file__).resolve().parent.parent
file_path = PROJECT_ROOT / "data" / "raw" / "house_prices.csv"

if not file_path.exists():
    raise FileNotFoundError(
        f"Dataset not found at: {file_path.resolve()}\n"
        "Check that the CSV is inside data/raw/."
    )

# Load dataset
df = pd.read_csv(file_path)

print("\n========== DWELLIQ: DATASET INSPECTION ==========")

print("\n1. DATASET SHAPE")
print(f"Total records: {df.shape[0]:,}")
print(f"Total columns: {df.shape[1]}")

print("\n2. COLUMN NAMES")
for column in df.columns:
    print(f"- {column}")

print("\n3. FIRST FIVE RECORDS")
print(df.head().to_string())

print("\n4. DATA TYPES")
print(df.dtypes.to_string())

print("\n5. MISSING VALUES")
missing = df.isnull().sum()
print(missing[missing > 0].to_string() if missing.any() else "No missing values.")

print("\n6. DUPLICATE ROWS")
print(f"Duplicate rows: {df.duplicated().sum():,}")

print("\n7. NUMERICAL SUMMARY")
print(df.describe().T.to_string())

print("\n8. POSSIBLE PRICE AND LOCATION COLUMNS")
for column in df.columns:
    name = column.lower()
    if any(word in name for word in ["price", "cost", "amount", "location", "city", "locality"]):
        print(f"- {column}: {df[column].dropna().astype(str).head(5).tolist()}")

print("\n========== INSPECTION COMPLETE ==========")
