
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# --------------------------------------------------
# 1. PROJECT PATHS AND SETTINGS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_house_prices.csv"
MODEL_DIR = PROJECT_ROOT / "models"
REPORT_DIR = PROJECT_ROOT / "reports"

TARGET = "total_price_rupees"
RANDOM_STATE = 42


# --------------------------------------------------
# 2. LOAD AND VALIDATE DATA
# --------------------------------------------------

def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {DATA_PATH}\n"
            "Run src/data_preprocessing.py first."
        )

    df = pd.read_csv(DATA_PATH, low_memory=False)

    if TARGET not in df.columns:
        raise ValueError(f"Target column '{TARGET}' is missing.")

    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")
    df = df.dropna(subset=[TARGET])
    df = df[df[TARGET] > 0].copy()

    if len(df) < 10:
        raise ValueError("Not enough valid records to train and test.")

    print(f"Usable records: {len(df):,}")
    return df


# --------------------------------------------------
# 3. SELECT FEATURES AND TARGET
# --------------------------------------------------

def prepare_features(df):
    numeric_candidates = [
        "BHK",
        "carpet_area_sqft",
        "Bathroom",
        "Balcony",
    ]

    categorical_candidates = [
        "location",
        "Status",
        "Floor",
        "Transaction",
        "Furnishing",
        "facing",
        "Ownership",
        "Car Parking",
    ]

    numeric_features = [
        column for column in numeric_candidates if column in df.columns
    ]

    categorical_features = [
        column for column in categorical_candidates if column in df.columns
    ]

    if not numeric_features and not categorical_features:
        raise ValueError("No usable model features were found.")

    X = df[numeric_features + categorical_features].copy()
    y = df[TARGET].copy()

    # Convert numeric-looking columns safely.
    for column in numeric_features:
        X[column] = pd.to_numeric(X[column], errors="coerce")

    # Treat text and mixed-type categories consistently.
    for column in categorical_features:
        X[column] = X[column].astype("string").astype(object)
        X[column] = X[column].where(X[column].notna(), np.nan)

    print(f"Numeric features: {numeric_features}")
    print(f"Categorical features: {categorical_features}")

    return X, y, numeric_features, categorical_features


# --------------------------------------------------
# 4. BUILD PREPROCESSING PIPELINE
# --------------------------------------------------

def build_preprocessor(numeric_features, categorical_features):
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    min_frequency=10,
                    sparse_output=True,
                ),
            ),
        ]
    )

    transformers = []

    if numeric_features:
        transformers.append(
            ("numeric", numeric_pipeline, numeric_features)
        )

    if categorical_features:
        transformers.append(
            ("categorical", categorical_pipeline, categorical_features)
        )

    return ColumnTransformer(transformers=transformers)


# --------------------------------------------------
# 5. TRAIN, EVALUATE AND SAVE MODELS
# --------------------------------------------------

def train_models():
    df = load_data()
    X, y, numeric_features, categorical_features = prepare_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
    )

    print(f"\nTraining records: {len(X_train):,}")
    print(f"Testing records: {len(X_test):,}")

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=100,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    results = []
    fitted_models = {}

    for name, estimator in models.items():
        print(f"\nTraining {name}...")

        pipeline = Pipeline(
            steps=[
                (
                    "preprocessor",
                    build_preprocessor(
                        numeric_features,
                        categorical_features,
                    ),
                ),
                ("model", estimator),
            ]
        )

        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)

        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)

        results.append(
            {
                "Model": name,
                "MAE_Rupees": mae,
                "RMSE_Rupees": rmse,
                "R2": r2,
            }
        )

        fitted_models[name] = pipeline

        print(f"MAE:  ₹{mae:,.2f}")
        print(f"RMSE: ₹{rmse:,.2f}")
        print(f"R²:   {r2:.4f}")

    # MAE is the primary selection metric.
    results_df = pd.DataFrame(results).sort_values("MAE_Rupees")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    results_df.to_csv(
        REPORT_DIR / "model_comparison.csv",
        index=False,
    )

    best_name = results_df.iloc[0]["Model"]
    best_pipeline = fitted_models[best_name]

    joblib.dump(
        {
            "model": best_pipeline,
            "model_name": best_name,
            "target": TARGET,
            "feature_columns": X.columns.tolist(),
            "metrics": results_df.iloc[0].to_dict(),
        },
        MODEL_DIR / "best_model.joblib",
    )

    print("\n" + "=" * 55)
    print("DWELLIQ MODEL COMPARISON")
    print("=" * 55)
    print(results_df.to_string(index=False))
    print(f"\nSelected model: {best_name}")
    print(f"Model saved to: {MODEL_DIR / 'best_model.joblib'}")
    print(f"Comparison saved to: {REPORT_DIR / 'model_comparison.csv'}")


if __name__ == "__main__":
    train_models()
