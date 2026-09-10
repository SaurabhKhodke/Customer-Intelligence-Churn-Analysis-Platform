# SHAP Explainability — Customer Intelligence Project

## What This Document Covers
How SHAP (SHapley Additive exPlanations) is used in this project to explain
individual churn predictions, and precisely how to read positive/negative
SHAP values for this specific model.

## What SHAP Is
[DOMAIN KNOWLEDGE] SHAP is a model-explainability technique based on
cooperative game theory (Shapley values). It attributes a model's
prediction for a given input to each individual feature, quantifying how
much each feature pushed the prediction up or down relative to a baseline
(average) prediction.

## Why SHAP Is Used
[DOMAIN KNOWLEDGE] SHAP allows the platform to explain *why* a specific
customer received a specific churn probability — turning an otherwise
"black box" number into a feature-by-feature breakdown. This directly
supports the project's goal of providing customer-level, natural-language
explanations rather than a bare probability.

## What a SHAP Value Represents
[DOMAIN KNOWLEDGE] For a single customer and a single feature, the SHAP
value is the estimated contribution of that feature's value to the
difference between the model's prediction for this customer and the
model's average (baseline) prediction across the training data.

### Positive SHAP Value — For This Churn Model
[MODEL FACT — interpretation rule for this project] A **positive**
contribution pushes the prediction **toward churn** (increases predicted
churn probability relative to baseline).

### Negative SHAP Value — For This Churn Model
[MODEL FACT — interpretation rule for this project] A **negative**
contribution pushes the prediction **away from churn** (decreases predicted
churn probability relative to baseline, i.e., toward retention).

This direction is specific to how the model's positive class is defined
(`churn = 1`) — it is not a universal rule across all SHAP applications, see
below.

### Magnitude of a SHAP Value
[DOMAIN KNOWLEDGE] The magnitude (absolute size) of a SHAP value indicates
*how much* that feature moved the prediction, regardless of direction. A
SHAP value of `+1.985` had a larger effect on the prediction than one of
`+0.12`, even though both are positive (churn-pushing).

## Feature Contribution vs. Feature Importance
[DOMAIN KNOWLEDGE]
- **SHAP contribution (local):** How much a feature mattered for **one
  specific customer's** prediction. Can be positive or negative, and
  differs from customer to customer.
- **Feature importance (global):** How much a feature matters **on average
  across all customers/predictions** — typically summarized as the mean
  absolute SHAP value across the dataset. This is a single number per
  feature and does not show direction for any individual customer.

## Local Explanation vs. Global Explanation
[DOMAIN KNOWLEDGE]
- **Local explanation:** Explains one prediction — "why is *this* customer
  HIGH risk?" Uses that customer's individual SHAP values.
- **Global explanation:** Explains the model's overall behavior — "which
  features matter most across the whole customer base?" Uses aggregated
  SHAP values (e.g., mean absolute value per feature) across many
  customers.

## How SHAP Explains an Individual Customer
[DOMAIN KNOWLEDGE — illustrative, using this project's actual feature
names] Example: a customer with the following SHAP contributions toward
their churn prediction:

| Feature | Customer Value | SHAP Contribution | Direction |
|---|---|---|---|
| `orders_count` | 3 | +1.42 | Pushes toward churn |
| `support_tickets` | 4 | +0.88 | Pushes toward churn |
| `tenure_months` | 2 | +0.35 | Pushes toward churn |
| `monthly_spend` | 120 | -0.61 | Pushes away from churn |

**Interpretation:** This customer's low `orders_count`, elevated
`support_tickets`, and short `tenure_months` each pushed the prediction
toward higher churn probability, while their relatively high
`monthly_spend` pulled it back somewhat — but not enough to offset the
other signals. This is an illustrative example only, not an actual model
output.

## Explaining a HIGH-Risk Classification
[DOMAIN KNOWLEDGE] A customer is typically classified HIGH risk when the
*sum* of their SHAP contributions is strongly positive — i.e., several
features (or a few strongly weighted ones) push the prediction well above
the baseline. The explanation should name the top positive-contribution
features and describe, using the feature dictionary's business meaning, why
those values plausibly indicate risk.

## Explaining a LOW-Risk Classification
[DOMAIN KNOWLEDGE] A customer is typically classified LOW risk when the sum
of their SHAP contributions is strongly negative — features like high
recent order activity or high engagement pull the prediction well below
baseline. The explanation should name the top negative-contribution
features similarly.

## Why SHAP Values From Different Models Cannot Blindly Be Compared
[DOMAIN KNOWLEDGE] SHAP values are relative to a specific model's learned
function and baseline (expected value). Two different models — even on the
same data — can produce different SHAP values for the same customer,
because they learned different internal relationships. Comparing raw SHAP
magnitudes across models (e.g., Logistic Regression vs. a tree-based model)
without normalizing for scale/baseline can be misleading. Within this
project, SHAP comparisons should stay within a single trained model's
outputs.

## Guardrails for the LLM
[DOMAIN KNOWLEDGE]
- Always state direction correctly for this model: **positive = toward
  churn, negative = away from churn.**
- Do not describe a SHAP contribution as proof of causation — see
  `churn_concepts.md` on association vs. causation.
- Do not invent SHAP values — always source them from the actual
  customer-level explanation output, not from this document's illustrative
  example.
