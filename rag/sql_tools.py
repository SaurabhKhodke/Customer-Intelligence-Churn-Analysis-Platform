import re
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "customer_churn.db"

ALLOWED_TABLES = {"customers", "customer_predictions"}
MAX_ROWS = 100

DATABASE_SCHEMA = """
Database: customer_churn.db

Tables:

customers
- customer_id INTEGER
- age REAL
- gender TEXT
- city TEXT
- acquisition_channel TEXT
- subscription_plan TEXT
- payment_method TEXT
- signup_date TIMESTAMP
- tenure_months INTEGER
- orders_count INTEGER
- monthly_spend REAL
- discount_usage_rate REAL
- support_tickets INTEGER
- satisfaction_score INTEGER
- last_order_date TIMESTAMP
- churn INTEGER
- recency_days INTEGER
- orders_per_month REAL
- support_tickets_per_month REAL

customer_predictions
- customer_id INTEGER
- churn_probability REAL
- predicted_churn INTEGER
- risk TEXT
- model_version TEXT
- predicted_at TEXT

Relationship: customers.customer_id = customer_predictions.customer_id
"""


def get_connection():
    """Open the database in SQLite read-only mode."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    connection = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def validate_sql(sql: str) -> tuple[bool, str]:
    """Validate and normalize a generated query before execution."""
    if not sql or not sql.strip():
        return False, "SQL query is empty."

    sql = sql.strip()
    sql = re.sub(r"^```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*```$", "", sql).strip()

    if not re.fullmatch(r"SELECT\b[\s\S]*", sql, flags=re.IGNORECASE):
        return False, "Only SELECT queries are allowed."

    # One optional final semicolon only.
    body = sql.rstrip(";").strip()
    if ";" in body:
        return False, "Multiple SQL statements are not allowed."

    # Reject SQL comments so hidden trailing statements/instructions cannot be smuggled in.
    if "--" in body or "/*" in body or "*/" in body:
        return False, "SQL comments are not allowed."

    forbidden_keywords = (
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
        "REPLACE", "TRUNCATE", "ATTACH", "DETACH", "VACUUM", "PRAGMA",
    )
    for keyword in forbidden_keywords:
        if re.search(rf"\b{keyword}\b", body, re.IGNORECASE):
            return False, f"Forbidden SQL operation detected: {keyword}"

    # Reject CTEs and non-table FROM/JOIN targets; the generated SQL should use only the two known tables.
    table_matches = re.findall(
        r"\b(?:FROM|JOIN)\s+[\"`]?([A-Za-z_][A-Za-z0-9_]*)[\"`]?",
        body,
        flags=re.IGNORECASE,
    )
    if not table_matches:
        return False, "The query must read from an allowed project table."

    for table in table_matches:
        if table.lower() not in ALLOWED_TABLES:
            return False, f"Table '{table}' is not allowed."

    if re.search(r"\b(?:WITH|UNION|INTERSECT|EXCEPT)\b", body, re.IGNORECASE):
        return False, "CTEs and set-operation queries are not allowed."

    # Bound ordinary row-returning queries. Aggregates can return one/few rows naturally.
    if "LIMIT" not in body.upper() and not re.search(
        r"\b(COUNT|AVG|SUM|MIN|MAX)\s*\(", body, re.IGNORECASE
    ):
        body += f" LIMIT {MAX_ROWS}"

    return True, body


def execute_sql(sql: str) -> dict:
    """Validate and execute a read-only project SQL query."""
    is_valid, validated_sql = validate_sql(sql)
    if not is_valid:
        return {"success": False, "error": validated_sql, "sql": sql}

    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(validated_sql)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        result_rows = [dict(row) for row in rows]

        return {
            "success": True,
            "sql": validated_sql,
            "columns": columns,
            "rows": result_rows,
            "row_count": len(result_rows),
        }
    except sqlite3.Error as exc:
        return {"success": False, "error": f"SQLite error: {exc}", "sql": validated_sql}
    finally:
        if connection is not None:
            connection.close()


def get_database_schema() -> str:
    return DATABASE_SCHEMA


def get_schema_for_llm() -> str:
    """Return the exact allow-listed schema used by the SQL generator."""
    return DATABASE_SCHEMA
