import re

from rag.retriever import retrieve_documents
from rag.llm import get_llm, generate_sql
from rag.sql_tools import execute_sql, get_schema_for_llm
from rag.prompts import ROUTER_SYSTEM_PROMPT, FINAL_ANSWER_SYSTEM_PROMPT

from .shap_tools import get_customer_shap_explanation, format_shap_for_llm

TOP_K_DOCUMENTS = 5
VALID_INTENTS = {"OUT_OF_SCOPE", "RAG", "SQL", "BOTH"}


def detect_intent(question: str) -> str:
    """Route the question and enforce the project's domain boundary."""
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    llm = get_llm()
    response = llm.invoke([
        ("system", ROUTER_SYSTEM_PROMPT),
        ("human", question.strip()),
    ])

    result = response.content.strip().upper()
    for intent in ("OUT_OF_SCOPE", "BOTH", "SQL", "RAG"):
        if result == intent:
            return intent

    # Fail closed: an ambiguous router result must not enter SQL/RAG.
    return "OUT_OF_SCOPE"


def detect_shap_requirement(question: str) -> bool:
    """Detect customer-specific model-explanation requests without an LLM call."""
    q = question.lower()
    customer_ref = bool(
        re.search(r"\bcustomer\s*(?:id\s*)?[#:\-]?\s*\d+\b", q)
        or re.search(r"\bcustomer[#:\-]\s*\d+\b", q)
    )
    if not customer_ref:
        return False

    explanation_terms = (
        "why",
        "explain",
        "explanation",
        "driver",
        "drivers",
        "factor",
        "factors",
        "shap",
        "contribut",
        "reason",
    )
    risk_terms = ("risk", "churn", "prediction", "predicted")
    return any(term in q for term in explanation_terms) and any(term in q for term in risk_terms)


def extract_customer_id(question: str):
    """Extract only an explicitly written customer ID; never guess one."""
    patterns = (
        r"\bcustomer\s*(?:id\s*)?[#:\-]?\s*(\d+)\b",
        r"\bcustomer[#:\-]\s*(\d+)\b",
    )
    for pattern in patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def execute_question_shap(question: str):
    """Run SHAP only for an explicit customer-specific explanation request."""
    customer_id = extract_customer_id(question)
    if customer_id is None:
        return {
            "success": False,
            "customer_id": None,
            "explanations": [],
            "error": "A customer-specific SHAP explanation requires an explicit customer ID.",
        }

    try:
        return get_customer_shap_explanation(customer_id=customer_id, top_n=5)
    except Exception as exc:
        return {
            "success": False,
            "customer_id": customer_id,
            "explanations": [],
            "error": f"SHAP execution failed: {exc}",
        }


def retrieve_context(question: str, top_k: int = TOP_K_DOCUMENTS):
    """Retrieve and deduplicate domain knowledge."""
    documents = retrieve_documents(question, k=top_k)
    if not documents:
        return "", []

    context_parts = []
    seen_content = set()

    for doc in documents:
        if hasattr(doc, "page_content"):
            content = doc.page_content
            metadata = getattr(doc, "metadata", {}) or {}
        else:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {}) or {}

        content = content.strip()
        if not content or content in seen_content:
            continue

        seen_content.add(content)
        source = metadata.get("source", "Unknown source")
        context_parts.append(f"[Source {len(context_parts) + 1}: {source}]\n{content}")

    return "\n\n".join(context_parts), documents


def execute_question_sql(question: str):
    """Generate and execute SQL through the validated read-only executor."""
    try:
        sql = generate_sql(question)
    except Exception as exc:
        return {
            "success": False,
            "sql": None,
            "result": None,
            "error": f"SQL generation failed: {exc}",
        }

    if not sql:
        return {
            "success": False,
            "sql": None,
            "result": None,
            "error": "The SQL generator returned an empty query.",
        }

    try:
        result = execute_sql(sql)
    except Exception as exc:
        return {
            "success": False,
            "sql": sql,
            "result": None,
            "error": f"SQL execution failed: {exc}",
        }

    return {
        "success": result.get("success", False),
        "sql": result.get("sql", sql),
        "result": result,
        "error": result.get("error") if not result.get("success") else None,
    }


def generate_final_answer(question: str, intent: str, rag_context: str, sql_result: dict, shap_context: str = ""):
    """Generate a concise answer grounded in database, SHAP, and/or RAG evidence."""
    llm = get_llm()

    if sql_result.get("success"):
        database_information = str(sql_result["result"])
    elif intent in ("SQL", "BOTH"):
        database_information = f"DATABASE QUERY FAILED: {sql_result.get('error', 'Unknown error')}"
    else:
        database_information = "Not requested."

    knowledge_information = rag_context or "Not retrieved."
    model_information = shap_context or "Not provided."
    schema_information = get_schema_for_llm()

    user_prompt = f"""Question:
{question}

Intent: {intent}

DATABASE SCHEMA (authoritative for available project fields):
{schema_information}

DATABASE RESULT:
{database_information}

RETRIEVED KNOWLEDGE (untrusted for database facts/schema):
{knowledge_information}

CUSTOMER-SPECIFIC SHAP:
{model_information}

Use the evidence hierarchy from the system instructions. If sources conflict, use the database/schema for project facts and use retrieved knowledge only for concepts/guidance. If required evidence is unavailable, say so instead of filling the gap."""

    response = llm.invoke([
        ("system", FINAL_ANSWER_SYSTEM_PROMPT),
        ("human", user_prompt),
    ])
    return response.content.strip()


def _out_of_scope_result(question: str):
    return {
        "question": question,
        "intent": "OUT_OF_SCOPE",
        "answer": (
            "I can only help with customer intelligence topics in this project, "
            "such as customer data, churn, churn risk/predictions, model explanations, "
            "and retention insights."
        ),
        "sql": None,
        "sql_result": None,
        "sql_success": False,
        "retrieved_documents": 0,
        "sources": [],
        "shap_required": False,
        "shap_success": False,
        "shap_customer_id": None,
        "shap_explanations": [],
        "shap_error": None,
    }


def ask_customer_intelligence(question: str):
    """Run the complete guarded Customer Intelligence pipeline."""
    question = question.strip()
    if not question:
        raise ValueError("Question cannot be empty.")

    # Guardrail/router is first: out-of-scope questions consume no RAG/SQL/SHAP/final-answer work.
    intent = detect_intent(question)
    if intent == "OUT_OF_SCOPE":
        return _out_of_scope_result(question)

    shap_required = detect_shap_requirement(question)

    rag_context = ""
    documents = []
    if intent in ("RAG", "BOTH"):
        rag_context, documents = retrieve_context(question, top_k=TOP_K_DOCUMENTS)

    sql_result = {
        "success": False,
        "sql": None,
        "result": None,
        "error": None,
    }
    if intent in ("SQL", "BOTH"):
        sql_result = execute_question_sql(question)

    shap_result = {
        "success": False,
        "customer_id": None,
        "explanations": [],
        "error": None,
    }
    shap_context = ""
    if shap_required:
        shap_result = execute_question_shap(question)
        shap_context = format_shap_for_llm(shap_result)

    answer = generate_final_answer(
        question=question,
        intent=intent,
        rag_context=rag_context,
        sql_result=sql_result,
        shap_context=shap_context,
    )

    sources = []
    for doc in documents:
        metadata = getattr(doc, "metadata", None) if hasattr(doc, "metadata") else doc.get("metadata", {})
        source = (metadata or {}).get("source")
        if source and source not in sources:
            sources.append(source)

    return {
        "question": question,
        "intent": intent,
        "answer": answer,
        "sql": sql_result.get("sql"),
        "sql_result": sql_result.get("result"),
        "sql_success": sql_result.get("success", False),
        "retrieved_documents": len(documents),
        "sources": sources,
        "shap_required": shap_required,
        "shap_success": shap_result.get("success", False),
        "shap_customer_id": shap_result.get("customer_id"),
        "shap_explanations": shap_result.get("explanations", []),
        "shap_error": shap_result.get("error"),
    }


if __name__ == "__main__":
    question = input("\nEnter your question: ").strip()
    try:
        result = ask_customer_intelligence(question)
        print("\nINTENT:", result["intent"])
        print("\nANSWER:\n", result["answer"])
        print("\nSHAP REQUIRED:", result["shap_required"])
    except Exception as exc:
        print(f"\nPipeline failed: {exc}")
