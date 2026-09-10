# Dataset Overview — Customer Intelligence / Churn Prediction

## What This Document Covers
This document explains the purpose, structure, and boundaries of the customer
dataset used by the Customer Intelligence platform. It is written to be
retrieved independently — if only this section is returned to the LLM, it
should still be enough to understand what the dataset is and is not.

## Purpose of the Dataset
[DATASET FACT] The dataset supports a customer churn prediction problem: for
each customer, the goal is to estimate the probability that the customer will
churn (stop being an active customer), and to classify that customer into a
LOW, MEDIUM, or HIGH risk category.

[DOMAIN KNOWLEDGE] In a churn intelligence platform, the dataset typically
serves three purposes: (1) training a predictive model, (2) supporting
descriptive/business analytics (e.g., churn rate by city), and (3) providing
the structured facts that an LLM layer can reference when explaining a
prediction. This project follows that same pattern.

## What One Customer Record Represents
[DATASET FACT] Each row in the dataset represents a single, unique customer,
identified by `customer_id`. All other fields describe attributes of that one
customer at the time the data was extracted (demographics, account tenure,
spending, order activity, support history) plus the outcome label `churn`.

## Dataset Size
[DATASET FACT] The broader Customer Intelligence application (per the project
architecture) operates against a customer base of approximately 100,000
customers stored in SQLite. This RAG knowledge base does **not** contain those
customer records — see `rag_boundaries.md` for why.

## Target Variable
[DATASET FACT] The target variable is `churn`, a binary label indicating
whether a customer has churned.
- `churn = 1` → the customer churned
- `churn = 0` → the customer did not churn (in the observed period)

[DOMAIN KNOWLEDGE] The exact definition of "churned" (e.g., no purchase in N
days, subscription cancellation, account closure) determines how the label
was generated. That operational definition has not been supplied for this
project and should not be assumed — if asked, the system should say the
precise churn-labeling rule is not documented rather than guessing.

## The Prediction Problem
[DATASET FACT] This is a **binary classification** problem at the
customer level: given a customer's features, predict the probability of
`churn = 1`. That probability is then mapped to a risk category (see
`risk_levels.md`) and can be explained feature-by-feature using SHAP (see
`shap_explainability.md`).

## Types of Variables

### Categorical vs. Numerical
[DATASET FACT]
- **Categorical:** `gender`, `city`
- **Numerical:** `age`, `tenure_months`, `monthly_spend`, `orders_count`,
  `support_tickets`
- **Date/time:** `last_order_date`
- **Identifier (not predictive):** `customer_id`
- **Target:** `churn`

### Raw vs. Derived Features
[DATASET FACT] All fields listed above are **raw** fields, i.e., they were
present in the source dataset described in the project brief rather than
computed from other fields.

[DOMAIN KNOWLEDGE — SUGGESTED, NOT YET CONFIRMED] It is common practice in
churn modeling to engineer additional **derived** features from raw fields,
such as recency (days since `last_order_date`) or order frequency
(`orders_count` relative to `tenure_months`). This knowledge base documents a
small set of such candidate derived features in `feature_dictionary.md`,
clearly labeled as suggestions rather than confirmed dataset facts, because
the final feature engineering has not been supplied.

## What the Dataset Can Answer
[DOMAIN KNOWLEDGE] Given the raw fields above, the dataset can support
questions such as:
- How does spending or order activity differ between churned and
  non-churned customers?
- Does churn rate vary by city or gender?
- Is there a relationship between tenure and churn?
- Is there a relationship between support ticket volume and churn?

## What the Dataset Cannot Answer
[DOMAIN KNOWLEDGE] Based on the fields currently defined, the dataset cannot
directly answer questions that depend on information it does not contain,
for example:
- Why a specific customer is dissatisfied (no satisfaction/sentiment field
  is defined)
- What acquisition channel brought in a customer (no acquisition field is
  defined)
- What a customer's subscription plan or product tier is (not defined)
- Product-level or transaction-level detail behind `orders_count` or
  `monthly_spend` (only aggregate figures are defined)

If a question requires one of these, the correct answer is that the
information is not present in the current schema — not a guess.

## Important Assumptions
[DOMAIN KNOWLEDGE] Until confirmed otherwise:
- Each customer appears once (one row per `customer_id`).
- `monthly_spend` is assumed to be a recent/representative average spend
  figure rather than a historical time series (no explicit definition of the
  averaging window has been supplied).
- `last_order_date` is assumed to be the date of the customer's most recent
  order as of data extraction.

## Dataset Limitations
[DOMAIN KNOWLEDGE]
- No satisfaction, sentiment, or complaint-content field is defined —
  interpretations of "customer happiness" cannot rely on this dataset alone.
- No acquisition-channel or marketing-source field is defined.
- No product/category-level detail is defined — spend and orders are
  aggregate counts.
- Sample size, class balance (churn vs. non-churn ratio), and any missing
  data profile have not been supplied and should not be assumed or invented.
