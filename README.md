# DwellIQ — Smart Property Estimates 🏡

A modern, machine learning-powered real estate price valuation web application built with Python, Scikit-Learn, and Streamlit.

---

## 🌟 Key Features
- **Modern Luxury Aesthetic**: Warm ivory background with forest & sage green accents, responsive layouts, subtle shadows, and a custom architectural hero banner.
- **Random Forest Machine Learning Pipeline**: Scikit-Learn `ColumnTransformer` with median/frequent imputation, one-hot encoding with unknown handling, and ensemble regression.
- **Multi-Signal Valuation**: Evaluates 12 property dimensions including location (80+ Indian cities), BHK configuration, carpet area, bathrooms, balconies, floor level, furnishing, facing, transaction type, and parking.
- **Indian Real Estate Denominations**: Formats estimates in Lakhs (₹ Lakh) and Crores (₹ Cr) along with typical error variance boundaries.
- **Transparent Academic Metrics**: Honest evaluation metrics displaying Mean Absolute Error (MAE), RMSE, and R² determination score.

---

## 🚀 How to Run the App

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the Streamlit web application**:
   ```bash
   python -m streamlit run app.py
   ```
   Or:
   ```bash
   streamlit run app.py
   ```

3. Open your browser at `http://localhost:8501`.

---

## 📂 Project Structure
```
DwellIQ/
├── app.py                 # Streamlit web application interface
├── requirements.txt       # Project python dependencies
├── assets/                # App assets & luxury home hero visual
│   └── luxury_home.jpg
├── data/
│   ├── raw/               # Raw real estate listings (house_prices.csv)
│   └── processed/         # Cleaned preprocessed dataset
├── models/
│   └── best_model.joblib  # Trained Scikit-Learn pipeline bundle
├── reports/
│   ├── figures/           # EDA charts & distribution plots
│   └── model_comparison.csv # Performance benchmarks
├── src/
│   ├── data_preprocessing.py # Data cleaning and transformation
│   └── train_model.py     # Model training and evaluation
└── tests/
    └── test_preprocessing.py
```
