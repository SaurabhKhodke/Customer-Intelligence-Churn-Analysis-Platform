# Customer Explanation Guidelines

## What This Document Covers
This is the operating guide for how the future LLM layer should construct
answers to customer-specific questions. It defines what information sources
to combine, and — critically — what the LLM must **not** do.

## The Four Information Sources to Combine
[DOMAIN KNOWLEDGE — system design guidance] For any customer-specific
question, the LLM should draw on up to four sources:

1. **Structured customer data from SQL** — the customer's actual field
   values (`age`, `gender`, `city`, `tenure_months`, `monthly_spend`,
   `orders_count`, `support_tickets`, `last_order_date`).
2. **Model prediction** — the customer's churn probability and risk
   category (LOW/MEDIUM/HIGH) from the ML layer.
3. **SHAP explanation** — the customer's individual, per-feature SHAP
   contributions from the explainability layer.
4. **Retrieved RAG knowledge** — the general definitions, meanings, and
   interpretation guidance contained in this knowledge base.

The RAG layer provides source (4) only. Sources (1)–(3) must come from the
live SQL/ML/SHAP outputs, never invented or assumed from this knowledge
base — see `rag_boundaries.md`.

## Core Rule: The LLM Must Not Invent Customer Facts
[DOMAIN KNOWLEDGE] The LLM must only state facts about a specific customer
that are actually present in that customer's SQL data, model output, or
SHAP output. It must not fabricate values, infer unstated attributes
(e.g., satisfaction, which isn't in the schema), or assume information "is
probably" true for a customer without a supporting data point.

## Worked Example: Correct vs. Incorrect Explanation

**Given:**
- SQL: `recency_days = 223` (illustrative — assumes the suggested derived
  feature has been implemented)
- SHAP: `recency_days` contribution `= +1.985`

**Correct explanation style:**
> "The customer's high recency indicates a long period since the last
> purchase, and the positive SHAP contribution shows that this feature is
> pushing the model toward higher churn risk."

This is correct because it (a) states the actual data value's meaning, (b)
correctly applies this project's SHAP sign convention (positive = toward
churn, per `shap_explainability.md`), and (c) does not add unsupported
claims.

**Incorrect explanation style:**
> "The customer is unhappy."

This is incorrect because satisfaction/happiness is not a field in this
dataset and is not something SHAP or the recency value can establish on
their own. Unless satisfaction or support data actually supports such a
statement (and even then, `support_tickets` measures volume, not
sentiment — see `feature_dictionary.md`), this claim should not be made.

## Guidelines by Question Type

### "Why is this customer high/low risk?"
Combine the customer's top SHAP contributions (by magnitude) with the
feature dictionary's business meaning for each, using correct SHAP-sign
interpretation (`shap_explainability.md`). State the risk category and
probability directly from the model output — don't re-derive or guess it.

### "What are the biggest churn drivers [for this customer]?"
Rank the customer's SHAP contributions by magnitude (not just positive
ones — largest absolute value first, then describe direction). Ground each
in the actual feature value from SQL, not a generic assumption.

### "What should we do to retain this customer?"
Map the customer's specific risk-elevating signals (from their SHAP output)
to the relevant entries in `retention_strategies.md`. Present these as
suggestions, explicitly non-guaranteed.

### "Which features are increasing / reducing churn risk [for this
customer]?"
Increasing = positive SHAP contributions for this model; reducing =
negative SHAP contributions. List them with their actual values, sourced
from the SHAP output — never estimate or infer them.

## Tone and Certainty
[DOMAIN KNOWLEDGE] Use probabilistic, signal-based language throughout
("may indicate," "is associated with," "the model estimates") rather than
definitive causal language ("is," "causes," "will"). See `churn_concepts.md`
for the association-vs-causation distinction this rule is built on.

## What Happens When Data Is Missing
[DOMAIN KNOWLEDGE] If a question requires a data point that isn't available
(e.g., a satisfaction score, or a specific customer's record that can't be
found), the LLM should state plainly that the information isn't available
rather than filling the gap with a plausible-sounding guess.
