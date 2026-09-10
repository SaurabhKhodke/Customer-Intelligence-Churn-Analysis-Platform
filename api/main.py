# api/main.py

from fastapi import FastAPI, HTTPException , Query
from pydantic import BaseModel
import sqlite3
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware


from src.prediction import (
    load_model,
    get_customer_prediction,
    get_high_risk_customers,
    get_risk_summary,
    get_dashboard_summary,
    get_shap_explanation,
    get_prediction_explanation
)


from typing import Optional
from pydantic import BaseModel

from rag.rag_pipeline import ask_customer_intelligence

# FastAPI

app = FastAPI(
    title="Customer Intelligence API",
    description="Customer churn prediction and intelligence API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths

DB_PATH = "data/customer_churn.db"

# Load model ONCE

model = load_model()

# Input schema

class CustomerInput(BaseModel):

    age: float
    tenure_months: int
    orders_count: int
    monthly_spend: float
    discount_usage_rate: float
    support_tickets: int
    satisfaction_score: int

    recency_days: int
    orders_per_month: float
    support_tickets_per_month: float

    gender: str
    city: str
    acquisition_channel: str
    subscription_plan: str
    payment_method: str
    
class AIQueryRequest(BaseModel):
    question: str


# Health


@app.get("/health")
def health():

    conn = sqlite3.connect(DB_PATH)

    prediction_count = pd.read_sql_query(
        """
        SELECT COUNT(*) AS count
        FROM customer_predictions
        """,
        conn
    ).iloc[0]["count"]

    conn.close()

    return {
        "status": "healthy",
        "model": "LogisticRegression",
        "stored_predictions": int(prediction_count)
    }



# POST /predict


@app.post("/predict")
def predict(customer: CustomerInput):

    input_df = pd.DataFrame(
        [customer.model_dump()]
    )

    probability = model.predict_proba(
        input_df
    )[0][1]

    if probability >= 0.70:
        risk = "HIGH"

    elif probability >= 0.40:
        risk = "MEDIUM"

    else:
        risk = "LOW"
        
    top_factors = get_prediction_explanation(customer.model_dump(), top_n=5)

    return {
        "churn_probability": round(
            float(probability),
            4
        ),
        "risk": risk,
        "top_factors": top_factors
    }



# GET /customer/{customer_id}


@app.get("/customer/{customer_id}")
def get_customer(customer_id: int):

    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT *
        FROM customers
        WHERE customer_id = ?
    """

    customer = pd.read_sql_query(
        query,
        conn,
        params=(customer_id,)
    )

    conn.close()

    if customer.empty:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    # Get stored prediction
    prediction = get_customer_prediction(
        customer_id
    )

    result = customer.iloc[0].to_dict()

    # Don't expose actual historical churn
    result.pop("churn", None)

    if prediction:

        result["churn_probability"] = round(
            float(
                prediction["churn_probability"]
            ),
            4
        )

        result["predicted_churn"] = int(
            prediction["predicted_churn"]
        )

        result["risk"] = prediction["risk"]

    return result



# GET /customers/high-risk


@app.get("/customers/high-risk")
def high_risk_customers(
    limit: int = Query(
        100,
        ge=1,
        le=500
    ),
    offset: int = Query(
        0,
        ge=0
    )
):

    customers, total = get_high_risk_customers(
        limit=limit,
        offset=offset
    )

    return {
        "total_high_risk_customers": total,
        "limit": limit,
        "offset": offset,
        "returned": len(customers),
        "customers": customers.to_dict(
            orient="records"
        )
    }


# GET /customers/risk-summary

@app.get("/customers/risk-summary")
def risk_summary():

    summary = get_risk_summary()

    result = {}

    for _, row in summary.iterrows():

        result[row["risk"]] = int(
            row["customer_count"]
        )

    return {
        "total_customers": sum(
            result.values()
        ),
        "risk_distribution": result
    }

# GET /dashboard/summary

@app.get("/dashboard/summary")
def dashboard_summary():

    summary = get_dashboard_summary()

    return {
        "total_customers": int(
            summary["total_customers"]
        ),

        "predicted_churn_customers": int(
            summary["predicted_churn_customers"]
        ),

        "average_churn_probability": round(
            float(
                summary["average_churn_probability"]
            ),
            4
        ),

        "high_risk_customers": int(
            summary["high_risk_customers"]
        ),

        "medium_risk_customers": int(
            summary["medium_risk_customers"]
        ),

        "low_risk_customers": int(
            summary["low_risk_customers"]
        )
    }

# GET /customers/{customer_id}/explanation

@app.get("/customers/{customer_id}/explanation")
def customer_explanation(customer_id: int):

    
    # Get stored prediction


    prediction = get_customer_prediction(
        customer_id
    )

    if prediction is None:

        raise HTTPException(
            status_code=404,
            detail="Customer prediction not found"
        )

    # SHAP explanation

    explanation = get_shap_explanation(
        customer_id,
        top_n=5
    )

    if explanation is None:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return {

        "customer_id": customer_id,

        "churn_probability": round(
            float(
                prediction[
                    "churn_probability"
                ]
            ),
            4
        ),

        "risk": prediction["risk"],

        "top_factors": explanation,

        "explanation_method": "SHAP"
    }
    
@app.post("/ai/query")
def ai_query(request: AIQueryRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    try:
        result = ask_customer_intelligence(request.question)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI query failed: {str(e)}"
        )   