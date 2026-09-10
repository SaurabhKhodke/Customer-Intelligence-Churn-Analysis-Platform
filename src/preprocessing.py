from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "customer_churn_raw.csv"
PROCESSED_DATA_PATH = (
    BASE_DIR / "data" / "processed" / "customer_churn_cleaned.csv"
)

TARGET = "churn"

NUMERICAL_FEATURES = [
    "age",
    "tenure_months",
    "orders_count",
    "monthly_spend",
    "discount_usage_rate",
    "support_tickets",
    "satisfaction_score",
    "recency_days",
    "orders_per_month",
    "support_tickets_per_month",
]

CATEGORICAL_FEATURES = [
    "gender",
    "city",
    "acquisition_channel",
    "subscription_plan",
    "payment_method",
]

MODEL_FEATURES = [
    "age",
    "gender",
    "city",
    "acquisition_channel",
    "subscription_plan",
    "payment_method",
    "tenure_months",
    "orders_count",
    "monthly_spend",
    "discount_usage_rate",
    "support_tickets",
    "satisfaction_score",
    "recency_days",
    "orders_per_month",
    "support_tickets_per_month",
]

REQUIRED_RAW_COLUMNS = [
    "customer_id",
    "age",
    "gender",
    "city",
    "acquisition_channel",
    "subscription_plan",
    "payment_method",
    "signup_date",
    "tenure_months",
    "orders_count",
    "monthly_spend",
    "discount_usage_rate",
    "support_tickets",
    "satisfaction_score",
    "last_order_date",
    TARGET,
]


def validate_raw_columns(df: pd.DataFrame) -> None:
    """Raise an error when required source columns are missing."""
    missing = [column for column in REQUIRED_RAW_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required raw columns: {missing}")


def load_data(file_path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw customer churn CSV."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Raw dataset not found: {path}")

    df = pd.read_csv(path)
    validate_raw_columns(df)
    return df


def clean_and_engineer(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and engineer features according to the EDA notebook."""
   
    df = df.copy()
    validate_raw_columns(df)

    # Remove exact duplicate rows.
    df = df.drop_duplicates().copy()

    # Notebook-defined missing-value handling.
    df["age"] = df["age"].fillna(df["age"].median())
    df["monthly_spend"] = df["monthly_spend"].fillna(df["monthly_spend"].median())

    gender_mode = df["gender"].mode()
    if gender_mode.empty:
        raise ValueError("Cannot impute gender because no non-null mode exists.")
    df["gender"] = df["gender"].fillna(gender_mode.iloc[0])
    df["city"] = df["city"].fillna("Unknown")

    # Parse dates exactly as in the notebook.
    df["signup_date"] = pd.to_datetime(df["signup_date"], dayfirst=True)
    df["last_order_date"] = pd.to_datetime(df["last_order_date"], dayfirst=True)

    # Standardize categorical values.
    for column in CATEGORICAL_FEATURES:
        df[column] = df[column].astype(str).str.strip()

    df["city"] = df["city"].str.title()

    # Fix clearly invalid values identified in the EDA notebook.
    age_median = df["age"].median()
    df.loc[df["age"] > 100, "age"] = age_median

    orders_median = df["orders_count"].median()
    df.loc[df["orders_count"] < 0, "orders_count"] = orders_median

    # Replace the specifically identified monthly-spend anomaly.
    anomalous_spend = df["monthly_spend"] == 999999
    if anomalous_spend.any():
        valid_spend_median = df.loc[~anomalous_spend, "monthly_spend"].median()
        df.loc[anomalous_spend, "monthly_spend"] = valid_spend_median

    # Correct logically invalid order dates before calculating recency.
    invalid_dates = df["last_order_date"] < df["signup_date"]
    df.loc[invalid_dates, "last_order_date"] = df.loc[
        invalid_dates, "signup_date"
    ]

    # The notebook defines frequency features using tenure_months.
    if (df["tenure_months"] <= 0).any():
        raise ValueError(
            "tenure_months contains zero/negative values; "
            "orders_per_month and support_tickets_per_month cannot be computed."
        )

    reference_date = df["last_order_date"].max()

    df["recency_days"] = (
        reference_date - df["last_order_date"]
    ).dt.days

    df["orders_per_month"] = (
        df["orders_count"] / df["tenure_months"]
    )

    df["support_tickets_per_month"] = (
        df["support_tickets"] / df["tenure_months"]
    )

    # The notebook explicitly removed this questionable feature.
    if "spend_per_order" in df.columns:
        df = df.drop(columns=["spend_per_order"])

    return df


def prepare_features(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.Series]:
    """Return model features X and target y."""
    missing_features = [
        feature for feature in MODEL_FEATURES if feature not in df.columns
    ]
    if missing_features:
        raise ValueError(f"Missing required model features: {missing_features}")

    if TARGET not in df.columns:
        raise ValueError(f"Missing target column: {TARGET}")

    X = df[MODEL_FEATURES].copy()
    y = df[TARGET].copy()
    return X, y


def validate_features(X: pd.DataFrame) -> bool:
    """Validate that every model input feature is present."""
    missing_features = [
        feature for feature in MODEL_FEATURES if feature not in X.columns
    ]
    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )
    return True


def preprocess_dataset(
    input_path: str | Path = RAW_DATA_PATH,
    output_path: str | Path = PROCESSED_DATA_PATH,
) -> pd.DataFrame:
    """Run the complete notebook-aligned preprocessing workflow and save it."""
    df = load_data(input_path)
    cleaned_df = clean_and_engineer(df)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(output, index=False)

    return cleaned_df


if __name__ == "__main__":
    processed = preprocess_dataset()
    print(f"Processed dataset saved to: {PROCESSED_DATA_PATH}")
    print(f"Shape: {processed.shape}")
