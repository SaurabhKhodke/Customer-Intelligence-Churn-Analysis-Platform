import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from rag.sql_tools import get_schema_for_llm, execute_sql
from rag.prompts import build_sql_system_prompt

load_dotenv()

MODEL_NAME = "openai/gpt-oss-120b"


def get_llm():
    """Create and return the configured Groq chat model."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY was not found in the environment.")

    return ChatGroq(
        model=MODEL_NAME,
        api_key=api_key,
        temperature=0,
    )


def generate_sql(question: str) -> str:
    """Generate one read-only SQL query for an already-routed SQL question."""
    if not question or not question.strip():
        raise ValueError("SQL question cannot be empty.")

    llm = get_llm()
    schema = get_schema_for_llm()
    system_prompt = build_sql_system_prompt(schema)

    response = llm.invoke([
        ("system", system_prompt),
        ("human", question.strip()),
    ])

    sql = response.content.strip()
    if sql.startswith("```"):
        sql = sql.replace("```sql", "", 1).replace("```", "", 1).strip()

    return sql


def generate_and_execute_sql(question: str):
    """Generate SQL and execute it through the read-only SQL tool."""
    sql = generate_sql(question)
    result = execute_sql(sql)
    return {"question": question, "sql": sql, "result": result}


if __name__ == "__main__":
    print("=" * 60)
    print("GROQ SQL + DATABASE TEST")
    print("=" * 60)

    question = input("\nEnter your question: ").strip()
    output = generate_and_execute_sql(question)

    print("\nGenerated SQL:")
    print("-" * 60)
    print(output["sql"])

    print("\nDatabase Result:")
    print("-" * 60)
    result = output["result"]
    if result.get("success"):
        print("Columns:", result["columns"])
        print("Rows:", result["rows"])
    else:
        print("SQL execution failed:")
        print(result)
