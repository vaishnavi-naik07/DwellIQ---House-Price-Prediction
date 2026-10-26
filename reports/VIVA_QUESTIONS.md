# DwellIQ — Project Viva Voce & Presentation Guide

**Project Title:** DwellIQ — Smarter Estimates. Better Decisions.  
**Academic Title:** House Price Prediction Using Linear Regression and Random Forest  
**Domain:** Machine Learning, Applied Data Science & Secure Web Applications  

---

## 1. Project Summary for College Viva
DwellIQ is an end-to-end real estate valuation system designed for Indian urban housing markets. It integrates a scikit-learn machine learning pipeline trained on 187,000+ real estate records with a Streamlit interface styled in an aesthetic ivory and forest-green palette. The application incorporates a secure, salted PBKDF2 authentication subsystem and feature explainability visualizations to demonstrate practical, production-level software design.

---

## 2. Common Viva Questions & Model Answers

### Q1: What is the target variable and how did you handle messy real-world pricing strings?
**Answer:**  
The target variable is `total_price_rupees`. The raw dataset contained unstructured textual denominations such as `"42 Lac"` and `"1.4 Cr"`. We built a regular expression parser in `data_preprocessing.py` that maps:
- Lacs/Lakhs: Amount $\times 100,000$
- Crores/Cr: Amount $\times 10,000,000$  
Non-numerical advertisements or unparsable listings were dropped to prevent noisy target distortion.

---

### Q2: Why did Random Forest outperform Linear Regression?
**Answer:**  
Housing prices have complex, non-linear relationships. For example, moving from the 1st floor to the 10th floor in Mumbai has a very different price multiplier than in a Tier-2 city. Linear regression assumes additive linearity, whereas Random Forest constructs an ensemble of decorrelated decision trees that capture non-linear feature interactions and categorical thresholds without requiring extensive manual feature crossing.

---

### Q3: Why is the $R^2$ score relatively low (~0.026)?
**Answer:**  
This reflects the genuine nature of real estate datasets across 81 heterogeneous cities:
1. **Unobserved Variables:** Exact street location, builder brand, proximity to metro stations, view quality, and construction finishes are not captured in tabular columns.
2. **Extreme Price Dispersion:** Property prices range from ₹15 Lakh to ₹80 Crore.  
Rather than artificially pruning valid high-value listings to fabricate a high $R^2$, we present honest test metrics (MAE of ~₹18.16 Lakh) and display empirical variance intervals ($\hat{y} \pm \text{MAE}$) in the user interface.

---

### Q4: How is data leakage prevented between training and testing?
**Answer:**  
All preprocessing transformations (median imputation for numericals, most frequent imputation for categoricals, and one-hot encoding) are encapsulated inside a Scikit-Learn `ColumnTransformer` within a `Pipeline`. The transformer parameters are fitted strictly on the 80% training partition and applied identically to the held-out 20% test partition and live inference requests.

---

### Q5: How do you handle unseen cities or unseen floor values at prediction time?
**Answer:**  
The `OneHotEncoder` is configured with `handle_unknown="ignore"` and `min_frequency=10`. If a user inputs an unseen categorical value, the one-hot encoder outputs all zeros for that feature category instead of raising an unhandled exception, allowing the regression trees to base predictions on known features.

---

### Q6: How does the authentication system protect student and user data?
**Answer:**  
1. **Password Hashing:** Uses `hashlib.pbkdf2_hmac` with SHA-256 and 200,000 iterations along with a unique 16-byte cryptographically secure salt (`os.urandom(16)`). Plaintext passwords are never stored.
2. **SQL Injection Defense:** All queries to the SQLite database use parameterized SQL queries (`?` placeholders).
3. **Brute Force Protection:** In-memory rate limiting locks accounts temporarily after 5 repeated failures within 5 minutes.
4. **Data Isolation:** User saved estimates are linked by `user_id` foreign keys and filtered strictly to the active session.

---

### Q7: What are the limitations of Streamlit session state security?
**Answer:**  
Streamlit maintains session state per active WebSocket connection in the server process memory. While suitable for prototypes, student presentations, and internal enterprise dashboards, a public high-scale multi-tenant system would require JWT / HTTP-only secure cookie sessions backed by Redis or an OAuth 2.0 Identity Provider.
