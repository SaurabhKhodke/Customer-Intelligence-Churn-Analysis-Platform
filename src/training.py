from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.preprocessing import (
    CATEGORICAL_FEATURES,
    MODEL_FEATURES,
    NUMERICAL_FEATURES,
    TARGET,
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "customer_churn_cleaned.csv"
MODEL_PATH = BASE_DIR / "models" / "final_churn_model.pkl"
METRICS_PATH = BASE_DIR / "models" / "training_metrics.json"

RANDOM_STATE = 42
TEST_SIZE = 0.20
CV_FOLDS = 3
N_ITER = 15

FINAL_MODEL_NAME = "Logistic Regression"


def load_processed_data(
    file_path: str | Path = DATA_PATH,
) -> pd.DataFrame:
    """Load the cleaned/engineered dataset."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Processed dataset not found: {path}")

    df = pd.read_csv(path)

    required = MODEL_FEATURES + [TARGET]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Processed dataset is missing columns: {missing}")

    return df


def build_preprocessor() -> ColumnTransformer:
    """Build the exact preprocessing structure used in the notebook."""
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )


def build_baseline_models() -> Dict[str, Any]:
    """Return the five baseline candidate models from the notebook."""
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "XGBoost": _build_xgb_baseline(),
        "CatBoost": _build_catboost_baseline(),
        "LightGBM": _build_lgbm_baseline(),
    }


def _build_xgb_baseline():
    from xgboost import XGBClassifier

    return XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )


def _build_catboost_baseline():
    from catboost import CatBoostClassifier

    return CatBoostClassifier(
        iterations=200,
        depth=6,
        learning_rate=0.1,
        verbose=False,
        random_seed=RANDOM_STATE,
    )


def _build_lgbm_baseline():
    from lightgbm import LGBMClassifier

    return LGBMClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=-1,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbosity=-1,
    )


def build_pipeline(model) -> Pipeline:
    """Wrap a classifier with the shared preprocessing pipeline."""
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("model", model),
        ]
    )


def evaluate_model(model, X_test, y_test) -> Dict[str, float]:
    """Calculate the metrics used in the notebook."""
    y_pred = model.predict(X_test)
    y_probability = model.predict_proba(X_test)[:, 1]

    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_probability)),
    }


def run_baseline_comparison(X_train, X_test, y_train, y_test):
    """Train and evaluate the five notebook baseline models."""
    results = {}

    for name, model in build_baseline_models().items():
        pipeline = build_pipeline(model)
        pipeline.fit(X_train, y_train)
        results[name] = evaluate_model(pipeline, X_test, y_test)

    return results


def build_tuning_pipelines() -> Dict[str, Pipeline]:
    """Build the three pipelines tuned in the notebook."""
    return {
        "Logistic Regression": build_pipeline(
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            )
        ),
        "XGBoost": build_pipeline(
            _build_xgb_tuning_base()
        ),
        "CatBoost": build_pipeline(
            _build_catboost_tuning_base()
        ),
    }


def _build_xgb_tuning_base():
    from xgboost import XGBClassifier

    return XGBClassifier(
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )


def _build_catboost_tuning_base():
    from catboost import CatBoostClassifier

    return CatBoostClassifier(
        verbose=False,
        random_seed=RANDOM_STATE,
        thread_count=-1,
    )


def get_param_distributions() -> Dict[str, Dict[str, Any]]:
    """Return the exact randomized-search spaces from the notebook."""
    return {
        "Logistic Regression": {
            "model__C": np.logspace(-2, 1, 10),
            "model__solver": ["liblinear", "lbfgs"],
            "model__penalty": ["l2"],
        },
        "XGBoost": {
            "model__n_estimators": [100, 200, 300, 400],
            "model__max_depth": [3, 4, 5, 6, 8],
            "model__learning_rate": [0.01, 0.03, 0.05, 0.1],
            "model__subsample": [0.7, 0.8, 0.9, 1.0],
            "model__colsample_bytree": [0.7, 0.8, 0.9, 1.0],
            "model__min_child_weight": [1, 3, 5],
        },
        "CatBoost": {
            "model__iterations": [200, 300, 500],
            "model__depth": [4, 5, 6, 7, 8],
            "model__learning_rate": [0.01, 0.03, 0.05, 0.1],
            "model__l2_leaf_reg": [1, 3, 5, 7, 10],
            "model__border_count": [32, 64, 128],
        },
    }


def tune_models(X_train, y_train):
    """Tune the three models using the notebook's RandomizedSearchCV setup."""
    tuned_models = {}
    tuning_results = {}

    pipelines = build_tuning_pipelines()
    param_distributions = get_param_distributions()

    for name, pipeline in pipelines.items():
        search = RandomizedSearchCV(
            estimator=pipeline,
            param_distributions=param_distributions[name],
            n_iter=N_ITER,
            scoring="f1",
            cv=CV_FOLDS,
            random_state=RANDOM_STATE,
            n_jobs=-1,
            verbose=1,
        )

        search.fit(X_train, y_train)

        tuned_models[name] = search.best_estimator_
        tuning_results[name] = {
            "best_cv_f1": float(search.best_score_),
            "best_params": search.best_params_,
        }

    return tuned_models, tuning_results


def train_and_save_model(
    data_path: str | Path = DATA_PATH,
    model_path: str | Path = MODEL_PATH,
    metrics_path: str | Path = METRICS_PATH,
) -> Pipeline:
    """Train the final model and save it to disk."""
   
    df = load_processed_data(data_path)

    X = df[MODEL_FEATURES].copy()
    y = df[TARGET].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    baseline_results = run_baseline_comparison(
        X_train, X_test, y_train, y_test
    )

    tuned_models, tuning_results = tune_models(X_train, y_train)

    final_model = tuned_models[FINAL_MODEL_NAME]
    final_metrics = evaluate_model(final_model, X_test, y_test)

    model_output = Path(model_path)
    model_output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, model_output)

    metrics_output = Path(metrics_path)
    metrics_output.parent.mkdir(parents=True, exist_ok=True)

    metrics_payload = {
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "cv_folds": CV_FOLDS,
        "n_iter": N_ITER,
        "final_model": FINAL_MODEL_NAME,
        "baseline_results": baseline_results,
        "tuning_results": tuning_results,
        "final_test_metrics": final_metrics,
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "feature_count": len(MODEL_FEATURES),
    }

    with metrics_output.open("w", encoding="utf-8") as file:
        json.dump(metrics_payload, file, indent=2, default=str)

    return final_model


if __name__ == "__main__":
    model = train_and_save_model()
    print(f"Final model saved to: {MODEL_PATH}")