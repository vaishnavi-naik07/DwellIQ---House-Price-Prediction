# DwellIQ Exploratory Data Analysis Report

**Generated At:** 2026-10-26  
**Analyzed Records:** 187,531  
**Duplicate Rows:** 0  
**Valid Parsed Target Prices:** 177,847  

---

## Key EDA Findings

1. **Target Distribution & Outliers:**
   - Property prices span from affordable housing (₹15 Lakh – ₹45 Lakh) to ultra-luxury penthouses (₹20 Cr – ₹80 Cr).
   - Because real-world real estate has a high right-skewed tail, log-transformation and ensemble tree regressors (like Random Forest) naturally handle non-linear scaling better than ordinary least squares.

2. **Geographical Concentration:**
   - The top 5 metro hubs account for over 50% of listing volume: Mumbai, New Delhi, Bangalore, Pune, and Thane.
   - Significant median price variance exists across regions (e.g., Mumbai median price is substantially higher than Tier-2 cities).

3. **Feature Cardinality & Missingness:**
   - `Carpet Area` has ~43% missingness in raw text, which must be systematically handled via train-set median imputation.
   - Unused fields (`Dimensions`, `Plot Area`) were 100% empty and safely pruned during preprocessing.
   - 2 BHK and 3 BHK configurations constitute the vast majority of urban listings.

4. **Visualizations Generated in `reports/figures/`:**
   - `missing_values.png`: Audit of missing fields across dataset.
   - `price_distribution_log.png`: Log10 target price distribution.
   - `location_distribution.png`: Listing counts for top 15 cities.
   - `median_price_by_location.png`: Median price comparison across top 10 cities.
   - `bhk_distribution.png`: Bedroom frequency distribution.
