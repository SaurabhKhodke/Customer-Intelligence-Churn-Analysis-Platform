from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd
import shap


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "customer_churn.db"
MODEL_PATH = BASE_DIR / "models" / "final_churn_model.pkl"

MODEL_VERSION = "logistic_regression_v1"

FEATURE_COLUMNS = [
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
    "gender",
    "city",
    "acquisition_channel",
    "subscription_plan",
    "payment_method",
]


def load_model(model_path: str | Path = MODEL_PATH):
    """Load the persisted complete churn pipeline."""
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Model not found at: {path}")

    return joblib.load(path)


def _get_risk(probability: float) -> str:
    """Map model probability to the project's risk buckets."""
    if probability >= 0.70:
        return "HIGH"
    if probability >= 0.40:
        return "MEDIUM"
    return "LOW"


def generate_predictions(model, df: pd.DataFrame) -> pd.DataFrame:
    """Generate churn probabilities, predictions and risk categories."""
    missing = [column for column in FEATURE_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing prediction features: {missing}")

    X = df[FEATURE_COLUMNS].copy()
    probabilities = model.predict_proba(X)[:, 1]
    predicted_churn = (probabilities >= 0.5).astype(int)

    return pd.DataFrame(
        {
            "customer_id": df["customer_id"].values,
            "churn_probability": probabilities,
            "predicted_churn": predicted_churn,
            "risk": [_get_risk(float(p)) for p in probabilities],
        }
    )


def get_connection() -> sqlite3.Connection:
    """Open the application database."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at: {DB_PATH}")

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_prediction_table(connection: Optional[sqlite3.Connection] = None) -> None:
    """Create the prediction table if it does not exist."""
    owns_connection = connection is None
    if owns_connection:
        connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS customer_predictions (
                customer_id INTEGER PRIMARY KEY,
                churn_probability REAL NOT NULL,
                predicted_churn INTEGER NOT NULL,
                risk TEXT NOT NULL,
                model_version TEXT NOT NULL,
                predicted_at TIMESTAMP NOT NULL,
                FOREIGN KEY (customer_id)
                    REFERENCES customers(customer_id)
            )
            """
        )
        connection.commit()
    finally:
        if owns_connection:
            connection.close()


def generate_and_store_predictions(
    model_path: str | Path = MODEL_PATH,
) -> pd.DataFrame:
    """
    Load customers from SQLite, generate predictions and replace the
    prediction table contents.
    """
    model = load_model(model_path)

    with get_connection() as connection:
        customers = pd.read_sql_query(
            "SELECT * FROM customers",
            connection,
        )

    predictions = generate_predictions(model, customers)
    predictions["model_version"] = MODEL_VERSION
    predictions["predicted_at"] = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        create_prediction_table(connection)
        predictions.to_sql(
            "customer_predictions",
            connection,
            if_exists="replace",
            index=False,
        )

    return predictions


def get_customer_prediction(customer_id: int):
    """Return the stored prediction for one customer."""
    with get_connection() as connection:
        result = pd.read_sql_query(
            """
            SELECT
                customer_id,
                churn_probability,
                predicted_churn,
                risk,
                model_version,
                predicted_at
            FROM customer_predictions
            WHERE customer_id = ?
            """,
            connection,
            params=(customer_id,),
        )

    if result.empty:
        return None

    return result.iloc[0].to_dict()


def get_high_risk_customers(limit: int = 100, offset: int = 0):
    """Return high-risk customers ordered by predicted churn probability."""
    if limit < 1:
        raise ValueError("limit must be >= 1")
    if offset < 0:
        raise ValueError("offset must be >= 0")

    with get_connection() as connection:
        result = pd.read_sql_query(
            """
            SELECT
                customer_id,
                churn_probability,
                predicted_churn,
                risk
            FROM customer_predictions
            WHERE risk = 'HIGH'
            ORDER BY churn_probability DESC
            LIMIT ? OFFSET ?
            """,
            connection,
            params=(limit, offset),
        )

        total = pd.read_sql_query(
            """
            SELECT COUNT(*) AS count
            FROM customer_predictions
            WHERE risk = 'HIGH'
            """,
            connection,
        ).iloc[0]["count"]

    return result, int(total)


def get_risk_summary() -> pd.DataFrame:
    """Return the count of customers in each risk category."""
    with get_connection() as connection:
        return pd.read_sql_query(
            """
            SELECT
                risk,
                COUNT(*) AS customer_count
            FROM customer_predictions
            GROUP BY risk
            ORDER BY
                CASE risk
                    WHEN 'HIGH' THEN 1
                    WHEN 'MEDIUM' THEN 2
                    WHEN 'LOW' THEN 3
                END
            """,
            connection,
        )


def get_dashboard_summary() -> dict:
    """Return the prediction metrics used by the dashboard."""
    with get_connection() as connection:
        result = pd.read_sql_query(
            """
            SELECT
                COUNT(*) AS total_customers,
                SUM(
                    CASE
                        WHEN predicted_churn = 1 THEN 1
                        ELSE 0
                    END
                ) AS predicted_churn_customers,
                AVG(churn_probability) AS average_churn_probability,
                SUM(
                    CASE
                        WHEN risk = 'HIGH' THEN 1
                        ELSE 0
                    END
                ) AS high_risk_customers,
                SUM(
                    CASE
                        WHEN risk = 'MEDIUM' THEN 1
                        ELSE 0
                    END
                ) AS medium_risk_customers,
                SUM(
                    CASE
                        WHEN risk = 'LOW' THEN 1
                        ELSE 0
                    END
                ) AS low_risk_customers
            FROM customer_predictions
            """,
            connection,
        )

    return result.iloc[0].to_dict()


def _to_dense(matrix):
    """Convert sparse transformer output to a dense array when necessary."""
    if hasattr(matrix, "toarray"):
        return matrix.toarray()
    return np.asarray(matrix)


def _get_model_components(model):
    """Extract the fitted preprocessor and classifier from the saved pipeline."""
    if not hasattr(model, "named_steps"):
        raise ValueError("Saved model must be a sklearn Pipeline.")

    try:
        preprocessor = model.named_steps["preprocessor"]
        classifier = model.named_steps["model"]
    except KeyError as exc:
        raise ValueError(
            "Saved pipeline must contain 'preprocessor' and 'model' steps."
        ) from exc

    return preprocessor, classifier


def _extract_shap_values(shap_result) -> np.ndarray:
    """Normalize SHAP output for the binary Logistic Regression model."""
    values = np.asarray(shap_result.values)

    if values.ndim == 3:
        return values[0, :, 1]
    if values.ndim == 2:
        return values[0]

    raise ValueError(f"Unexpected SHAP shape: {values.shape}")


def _clean_feature_name(transformed_feature: str) -> str:
    """Remove sklearn transformer prefixes."""
    if "__" in transformed_feature:
        return transformed_feature.split("__", 1)[1]
    return transformed_feature


def _map_to_original_feature(
    transformed_feature: str,
    customer_columns,
):
    """Map one-hot transformed names back to their original feature."""
    clean_feature = _clean_feature_name(transformed_feature)

    if clean_feature in customer_columns:
        return clean_feature

    for feature in FEATURE_COLUMNS:
        if clean_feature.startswith(feature + "_"):
            return feature

    return clean_feature


def _build_individual_explanations(
    feature_names,
    shap_values,
    customer_df: pd.DataFrame,
    top_n: int,
):
    shap_df = pd.DataFrame(
        {
            "feature": feature_names,
            "shap_value": shap_values,
        }
    )

    shap_df["abs_shap"] = shap_df["shap_value"].abs()
    shap_df = shap_df.sort_values(
        "abs_shap",
        ascending=False,
    ).head(top_n)

    explanations = []

    for _, row in shap_df.iterrows():
        transformed_feature = row["feature"]
        shap_value = float(row["shap_value"])

        original_feature = _map_to_original_feature(
            transformed_feature,
            customer_df.columns,
        )

        actual_value = None
        if original_feature in customer_df.columns:
            actual_value = customer_df.iloc[0][original_feature]

        if shap_value > 0:
            direction = "increases churn risk"
        elif shap_value < 0:
            direction = "decreases churn risk"
        else:
            direction = "no meaningful impact"

        if hasattr(actual_value, "item"):
            actual_value = actual_value.item()

        explanations.append(
            {
                "feature": original_feature,
                "value": actual_value,
                "shap_value": round(shap_value, 4),
                "direction": direction,
            }
        )

    return explanations


def get_shap_explanation(customer_id: int, top_n: int = 5):
    """
    Generate an individual SHAP explanation for a customer.

    The customer is transformed with the same fitted preprocessing used by
    the saved model. A reproducible sample of up to 200 customers is used as
    the SHAP background, matching the production intent of the explainability
    notebook while avoiding a full-dataset explainer on every API request.
    """
    if top_n < 1:
        raise ValueError("top_n must be >= 1")

    model_pipeline = load_model()
    preprocessor, classifier = _get_model_components(model_pipeline)

    with get_connection() as connection:
        customer = pd.read_sql_query(
            """
            SELECT *
            FROM customers
            WHERE customer_id = ?
            """,
            connection,
            params=(customer_id,),
        )

        background = pd.read_sql_query(
            """
            SELECT *
            FROM customers
            ORDER BY customer_id
            LIMIT 200
            """,
            connection,
        )

    if customer.empty:
        return None

    X_customer = customer[FEATURE_COLUMNS].copy()
    X_background = background[FEATURE_COLUMNS].copy()

    customer_transformed = _to_dense(
        preprocessor.transform(X_customer)
    )
    background_transformed = _to_dense(
        preprocessor.transform(X_background)
    )

    feature_names = preprocessor.get_feature_names_out()

    explainer = shap.LinearExplainer(
        classifier,
        background_transformed,
    )

    shap_result = explainer(customer_transformed)
    shap_values = _extract_shap_values(shap_result)

    return _build_individual_explanations(
        feature_names=feature_names,
        shap_values=shap_values,
        customer_df=customer,
        top_n=top_n,
    )


def get_prediction_explanation(customer_dict: dict, top_n: int = 5):
    """
    Generate SHAP explanations for an in-memory customer dictionary.

    This is useful when the prediction service already has a customer record
    and does not need to query the customer row again.
    """
    if top_n < 1:
        raise ValueError("top_n must be >= 1")

    model_pipeline = load_model()
    preprocessor, classifier = _get_model_components(model_pipeline)

    customer_df = pd.DataFrame([customer_dict])

    missing = [column for column in FEATURE_COLUMNS if column not in customer_df]
    if missing:
        raise ValueError(f"Missing prediction features: {missing}")

    with get_connection() as connection:
        background = pd.read_sql_query(
            """
            SELECT *
            FROM customers
            ORDER BY customer_id
            LIMIT 200
            """,
            connection,
        )

    X_customer = customer_df[FEATURE_COLUMNS].copy()
    X_background = background[FEATURE_COLUMNS].copy()

    customer_transformed = _to_dense(
        preprocessor.transform(X_customer)
    )
    background_transformed = _to_dense(
        preprocessor.transform(X_background)
    )

    feature_names = preprocessor.get_feature_names_out()

    explainer = shap.LinearExplainer(
        classifier,
        background_transformed,
    )

    shap_result = explainer(customer_transformed)
    shap_values = _extract_shap_values(shap_result)

    return _build_individual_explanations(
        feature_names=feature_names,
        shap_values=shap_values,
        customer_df=customer_df,
        top_n=top_n,
    )


def get_global_shap_importance(
    data_path: str | Path = None,
    sample_size: int = 5000,
) -> pd.DataFrame:
    """
    Calculate global mean-absolute SHAP importance.

    This follows the explainability notebook's 5,000-row representative
    sample and uses the persisted model pipeline.
    """
    if sample_size < 1:
        raise ValueError("sample_size must be >= 1")

    model_pipeline = load_model()
    preprocessor, classifier = _get_model_components(model_pipeline)

    if data_path is None:
        data_path = BASE_DIR / "data" / "processed" / "customer_churn_cleaned.csv"

    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"Processed dataset not found: {path}")

    df = pd.read_csv(path)
    X = df[FEATURE_COLUMNS].copy()

    X_transformed = _to_dense(preprocessor.transform(X))
    feature_names = preprocessor.get_feature_names_out()

    n_samples = min(sample_size, len(X_transformed))
    X_shap = pd.DataFrame(
        X_transformed,
        columns=feature_names,
    ).sample(
        n=n_samples,
        random_state=42,
    )

    explainer = shap.LinearExplainer(
        classifier,
        X_shap,
    )

    shap_result = explainer(X_shap)
    shap_values = np.asarray(shap_result.values)

    if shap_values.ndim == 3:
        shap_values = shap_values[:, :, 1]
    elif shap_values.ndim != 2:
        raise ValueError(f"Unexpected SHAP shape: {shap_values.shape}")

    return (
        pd.DataFrame(
            {
                "feature": feature_names,
                "mean_abs_shap": np.abs(shap_values).mean(axis=0),
            }
        )
        .sort_values("mean_abs_shap", ascending=False)
        .reset_index(drop=True)
    )


if __name__ == "__main__":
    predictions = generate_and_store_predictions()
    print(f"Stored predictions: {len(predictions)}")