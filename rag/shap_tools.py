
import sqlite3
import math

from src.prediction import get_prediction_explanation


# Configuration

DB_PATH = "data/customer_churn.db"

DEFAULT_TOP_N = 5
MAX_TOP_N = 10


# Helpers


def _make_json_safe(value):
    """
    Convert values returned by pandas/numpy into JSON-safe
    Python values.
    """

    if value is None:
        return None

    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None

    return value


# Get customer data

def get_customer_for_shap(customer_id):
    """
    Retrieve the complete customer record required by the
    existing SHAP implementation.

    Returns:
        dict | None
    """

    conn = sqlite3.connect(DB_PATH)

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM customers
            WHERE customer_id = ?
            """,
            (customer_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        columns = [
            description[0]
            for description in cursor.description
        ]

        customer = dict(zip(columns, row))

        return customer

    finally:

        conn.close()


# SHAP explanation

def get_customer_shap_explanation(
    customer_id,
    top_n=DEFAULT_TOP_N
):
    """
    Generate the top SHAP contributors for a customer.

    Parameters
    ----------
    customer_id : int
        Customer whose prediction should be explained.

    top_n : int
        Number of strongest SHAP contributors to return.

    Returns
    -------
    dict
        Structured SHAP explanation suitable for the RAG
        pipeline and FastAPI response.
    """

    # Validate customer ID


    try:
        customer_id = int(customer_id)

    except (TypeError, ValueError):

        return {
            "success": False,
            "customer_id": customer_id,
            "explanations": [],
            "error": "Invalid customer_id."
        }

    # Validate top_n

    try:
        top_n = int(top_n)

    except (TypeError, ValueError):

        top_n = DEFAULT_TOP_N

    top_n = max(1, min(top_n, MAX_TOP_N))


    # Get customer

    customer = get_customer_for_shap(customer_id)

    if customer is None:

        return {
            "success": False,
            "customer_id": customer_id,
            "explanations": [],
            "error": (
                f"Customer {customer_id} was not found "
                "in the customers table."
            )
        }

    # Generate SHAP explanation

    try:

        explanations = get_prediction_explanation(
            customer,
            top_n=top_n
        )

    except Exception as e:

        return {
            "success": False,
            "customer_id": customer_id,
            "explanations": [],
            "error": f"SHAP calculation failed: {str(e)}"
        }

    # Make result JSON safe

    safe_explanations = []

    for explanation in explanations:

        safe_explanations.append({
            "feature": explanation.get("feature"),
            "value": _make_json_safe(
                explanation.get("value")
            ),
            "shap_value": _make_json_safe(
                explanation.get("shap_value")
            ),
            "direction": explanation.get("direction")
        })

    return {
        "success": True,
        "customer_id": customer_id,
        "top_n": len(safe_explanations),
        "explanations": safe_explanations
    }


# Convenience formatter

def format_shap_for_llm(shap_result):
    """
    Convert structured SHAP results into concise context
    that can be passed to the final LLM.

    This is intentionally factual. The LLM should explain
    the meaning rather than inventing causes.
    """

    if not shap_result.get("success"):

        return (
            "SHAP explanation unavailable. "
            f"Reason: {shap_result.get('error', 'Unknown error')}"
        )

    explanations = shap_result.get(
        "explanations",
        []
    )

    if not explanations:

        return "No SHAP contributors were available."

    lines = []

    lines.append(
        f"SHAP contributors for customer "
        f"{shap_result['customer_id']}:"
    )

    for item in explanations:

        feature = item.get("feature")
        value = item.get("value")
        shap_value = item.get("shap_value")
        direction = item.get("direction")

        lines.append(
            f"- Feature: {feature} | "
            f"Observed value: {value} | "
            f"SHAP value: {shap_value} | "
            f"Effect: {direction}"
        )

    return "\n".join(lines)


# Local test

if __name__ == "__main__":

    print("=" * 60)
    print("CUSTOMER INTELLIGENCE SHAP TOOL TEST")
    print("=" * 60)

    customer_id_input = input(
        "\nEnter customer ID: "
    ).strip()

    result = get_customer_shap_explanation(
        customer_id_input,
        top_n=5
    )

    print("\nSHAP RESULT")
    print("-" * 60)

    print(result)

    print("\nLLM CONTEXT")
    print("-" * 60)

    print(format_shap_for_llm(result))

    print("\n" + "=" * 60)
    print("SHAP TOOL TEST COMPLETED")
    print("=" * 60)