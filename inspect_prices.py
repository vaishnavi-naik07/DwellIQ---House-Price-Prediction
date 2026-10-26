
import pandas as pd
import re
from pathlib import Path

DATA_PATH = Path("data/raw/house_prices.csv")
df = pd.read_csv(DATA_PATH)

def convert_price(value):
    """Convert listing prices like 42 Lac and 1.40 Cr to rupees."""
    if pd.isna(value):
        return None

    text = str(value).strip().lower()
    text = text.replace(",", "").replace("₹", "").replace("inr", "").strip()

    match = re.search(r"(\d+(?:\.\d+)?)\s*(crore|crores|cr|lakh|lakhs|lac|lacs)", text)

    if match:
        number = float(match.group(1))
        unit = match.group(2)

        if unit in ["cr", "crore", "crores"]:
            return number * 10_000_000

        return number * 100_000

    # Handle plain numeric values if present
    try:
        return float(text)
    except ValueError:
        return None


df["total_price_rupees"] = df["Amount(in rupees)"].apply(convert_price)

print("\n========== DWELLIQ PRICE VALIDATION ==========")

print("\n1. ORIGINAL PRICE EXAMPLES")
print(df["Amount(in rupees)"].dropna().sample(
    min(15, df["Amount(in rupees)"].notna().sum()),
    random_state=42
).to_string(index=False))

print("\n2. CONVERTED PRICE EXAMPLES")
print(
    df[["Amount(in rupees)", "total_price_rupees"]]
    .dropna(subset=["total_price_rupees"])
    .head(15)
    .to_string(index=False)
)

print("\n3. TOTAL PRICE SUMMARY (RUPEES)")
print(df["total_price_rupees"].describe().to_string())

print("\n4. PRICE CONVERSION STATUS")
print("Total rows:", len(df))
print("Converted prices:", df["total_price_rupees"].notna().sum())
print("Missing/unparsed prices:", df["total_price_rupees"].isna().sum())
print("Zero or negative prices:", (df["total_price_rupees"] <= 0).sum())

print("\n5. PRICE-PER-SQFT COLUMN SUMMARY")
print(df["Price (in rupees)"].describe().to_string())

print("\n6. CARPET AREA EXAMPLES")
print(df["Carpet Area"].dropna().head(15).to_string(index=False))

print("\n7. LOCATION DISTRIBUTION")
print(df["location"].value_counts(dropna=False).head(20).to_string())

print("\n8. CHECK: TOTAL PRICE VS PRICE PER SQFT")
check = df[
    df["total_price_rupees"].notna()
    & df["Price (in rupees)"].notna()
    & (df["Price (in rupees)"] > 0)
].copy()

check["implied_area_sqft"] = (
    check["total_price_rupees"] / check["Price (in rupees)"]
)

print("Rows available for comparison:", len(check))
print("Implied area summary:")
print(check["implied_area_sqft"].describe(
    percentiles=[0.1, 0.25, 0.5, 0.75, 0.9]
).to_string())

print("\n9. SAMPLE COMPARISON")
print(
    check[
        [
            "Amount(in rupees)",
            "total_price_rupees",
            "Price (in rupees)",
            "Carpet Area",
            "implied_area_sqft",
            "location",
        ]
    ].head(15).to_string(index=False)
)

print("\n========== VALIDATION COMPLETE ==========")
