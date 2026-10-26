
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Paths
DATA_PATH = Path("data/raw/house_prices.csv")
OUTPUT_DIR = Path("reports/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_PATH)

print("=" * 55)
print("              DWELLIQ - DATA ANALYSIS")
print("=" * 55)

print(f"\nTotal listings: {len(df):,}")
print(f"Total columns: {len(df.columns)}")

# 1. Location distribution
print("\nTop 15 locations:")
print(df["location"].value_counts().head(15))

plt.figure(figsize=(10, 6))
df["location"].fillna("Unknown").value_counts().head(15).plot(kind="bar")
plt.title("Top 15 Property Listing Locations")
plt.xlabel("Location")
plt.ylabel("Number of Listings")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "location_distribution.png", dpi=150)
plt.close()

# 2. Missing values
missing = df.isnull().sum()
missing = missing[missing > 0].sort_values(ascending=False)

print("\nMissing values:")
print(missing.to_string())

plt.figure(figsize=(12, 6))
(missing / len(df) * 100).plot(kind="bar")
plt.title("Missing Values by Column")
plt.ylabel("Missing Values (%)")
plt.xticks(rotation=75, ha="right")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "missing_values.png", dpi=150)
plt.close()

# 3. Extract BHK from property title
df["Title"] = df["Title"].fillna("")
df["BHK"] = pd.to_numeric(
    df["Title"].str.extract(r"(\d+)\s*BHK", expand=False),
    errors="coerce"
)

print("\nBHK distribution:")
print(df["BHK"].value_counts().sort_index().to_string())

plt.figure(figsize=(9, 5))
df["BHK"].value_counts().sort_index().plot(kind="bar")
plt.title("Property Listings by BHK")
plt.xlabel("Bedrooms (BHK)")
plt.ylabel("Number of Listings")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "bhk_distribution.png", dpi=150)
plt.close()

# 4. Price per square foot distribution
price_sqft = pd.to_numeric(
    df["Price (in rupees)"], errors="coerce"
)

valid_prices = price_sqft[
    price_sqft.notna() & (price_sqft > 0)
]

if not valid_prices.empty:
    upper_limit = valid_prices.quantile(0.99)
    valid_prices = valid_prices[valid_prices <= upper_limit]

    plt.figure(figsize=(10, 5))
    plt.hist(valid_prices, bins=50, edgecolor="black")
    plt.title("Price per Square Foot Distribution")
    plt.xlabel("Price per Square Foot (₹)")
    plt.ylabel("Number of Listings")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "price_per_sqft_distribution.png", dpi=150)
    plt.close()

print("\nEDA completed successfully!")
print(f"Charts saved in: {OUTPUT_DIR.resolve()}")
