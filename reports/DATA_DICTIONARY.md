# DwellIQ Dataset & Quality Specification

**Project:** DwellIQ — Smarter Estimates. Better Decisions.  
**Dataset Reference:** Indian Real Estate Property Listings (`data/raw/house_prices.csv`)  
**Processed Target:** `data/processed/cleaned_house_prices.csv`  
**Total Raw Records:** 187,531 listings across 81 unique Indian urban locations.  

---

## 1. Provenance & Description
The raw dataset contains residential property sale listings aggregated across major Indian real estate markets (metropolitan, Tier-1, and Tier-2 cities). Each record represents an individual residential listing detailing architectural dimensions, pricing tokens, geographic identifiers, legal tenure, and convenience attributes.

---

## 2. Target Variable
- **Target Feature:** `total_price_rupees` (numeric float)
- **Source Feature:** `Amount(in rupees)`
- **Parsing Logic:** Raw values contain Indian financial denominations such as `"45 Lac"`, `"1.25 Cr"`, `"85 Lakhs"`, or `"3.4 Crore"`. The preprocessing pipeline parses numerical components and converts them strictly into absolute Indian Rupees ($\text{INR}$):
  - $1\text{ Lac} = 100,000\text{ INR}$
  - $1\text{ Cr} = 10,000,000\text{ INR}$
- **Units:** Indian National Rupee (₹)

---

## 3. Data Dictionary

| Feature Name | Source Column | Data Type | Representation | Imputation / Pipeline Transformation |
| :--- | :--- | :--- | :--- | :--- |
| `total_price_rupees` | `Amount(in rupees)` | Float | Continuous property sale price in ₹ | Target variable (unparsed/empty rows dropped) |
| `BHK` | `Title` | Numeric / Integer | Count of bedrooms (1–8+) extracted via regex `(\d+)\s*BHK` | Median Imputation |
| `carpet_area_sqft` | `Carpet Area` | Float | Usable net floor area in square feet | Median Imputation |
| `Bathroom` | `Bathroom` | Numeric / Float | Number of bathrooms (1–8) | Median Imputation |
| `Balcony` | `Balcony` | Numeric / Float | Number of balconies (0–5) | Median Imputation |
| `location` | `location` | Categorical / String | City / urban region (e.g., Mumbai, Bangalore, Pune) | Most Frequent Imputation + OneHotEncoder (`handle_unknown='ignore'`) |
| `Status` | `Status` | Categorical / String | Construction status: `"Ready to Move"`, `"Under Construction"` | Most Frequent Imputation + OneHotEncoder |
| `Floor` | `Floor` | Categorical / String | Floor level (`"1"`, `"2"`, `"Ground"`, `"Basement"`, etc.) | Most Frequent Imputation + OneHotEncoder |
| `Transaction` | `Transaction` | Categorical / String | `"Resale"` vs `"New Property"` | Most Frequent Imputation + OneHotEncoder |
| `Furnishing` | `Furnishing` | Categorical / String | `"Furnished"`, `"Semi-Furnished"`, `"Unfurnished"` | Most Frequent Imputation + OneHotEncoder |
| `facing` | `facing` | Categorical / String | Directional orientation: `"East"`, `"North"`, etc. | Most Frequent Imputation + OneHotEncoder |
| `Ownership` | `Ownership` | Categorical / String | Property legal tenure: `"Freehold"`, `"Leasehold"`, etc. | Most Frequent Imputation + OneHotEncoder |
| `Car Parking` | `Car Parking` | Categorical / String | Parking capacity: `"1"`, `"2"`, `"Covered"`, `"Open"`, etc. | Most Frequent Imputation + OneHotEncoder |

---

## 4. Dataset Quality & Missing Value Audit

- **Raw Dimensions:** 187,531 rows × 21 columns.
- **Completely Unpopulated Columns Dropped:** `Dimensions` (100% null) and `Plot Area` (100% null) were dropped as unusable.
- **Redundant Identity Fields Dropped:** `Index`, `Super Area`, `Society`, `overlooking`, `Description` dropped to avoid high sparsity or noise without direct standardized valuation signals.
- **Deduplication:** Preprocessing removes exact duplicate listing records.
- **Carpet Area Sparsity:** In raw data, ~43% of rows had unstated carpet area, which the preprocessing pipeline handles via median imputation grouped across the training set to prevent test leakage.
- **Outlier Reality & Academic Discussion:** Real estate data in India contains legitimate high-end properties (e.g. penthouses and luxury sea-facing residences priced at ₹10 Cr – ₹80 Cr). Arbitrarily discarding these biases models against prime markets; instead, fair train/test evaluation with robust metrics (MAE, RMSE, $R^2$) reflects true dispersion.
