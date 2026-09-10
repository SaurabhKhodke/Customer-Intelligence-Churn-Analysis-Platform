# Risk Levels — LOW / MEDIUM / HIGH

## What This Document Covers
How this project's churn probability output is classified into risk
categories, and how those categories should and should not be used.

## What Churn Probability Represents
[MODEL FACT] The model outputs a probability (a value between 0 and 1)
representing its estimate of the likelihood that a given customer will
churn, based on the patterns it learned from training data. For example, an
output of `churn_probability = 0.87` (as shown in the project's example API
response) means the model estimates an 87% likelihood of churn for that
customer, according to the patterns it has learned — not a certainty.

## Risk Categories
[DATASET FACT] The platform classifies customers into three risk
categories:
- **LOW**
- **MEDIUM**
- **HIGH**

## Exact Thresholds
[MODEL FACT — NOT SUPPLIED] The exact probability cutoffs that separate
LOW / MEDIUM / HIGH have not been provided for this project. **Do not
invent threshold values** (e.g., do not assume LOW = 0–0.3, MEDIUM =
0.3–0.7, HIGH = 0.7–1.0, or any other specific split). If asked for the
exact thresholds, the correct answer is that they are defined in the
prediction/API layer and should be looked up there, not assumed from this
document. Once the actual thresholds are supplied, this section should be
updated to state them exactly.

## How Probability Differs From Risk Category
[DOMAIN KNOWLEDGE] Probability is a continuous, precise number (e.g.,
0.87); risk category is a simplified bucket derived from that number for
easier business communication. Two customers in the same risk bucket (e.g.,
both "HIGH") can still have meaningfully different underlying
probabilities (e.g., 0.71 vs. 0.98) — the category alone doesn't capture
that difference. When precision matters, prefer citing the actual
probability over just the category.

## How Risk Categories Should Be Interpreted
[DOMAIN KNOWLEDGE]
- **LOW risk:** The model estimates a relatively low likelihood of churn
  for this customer based on their current feature values.
- **MEDIUM risk:** The model estimates a middling likelihood — worth
  monitoring, not necessarily urgent.
- **HIGH risk:** The model estimates a relatively high likelihood of
  churn — typically the priority group for retention action.

These are model estimates, not guarantees, and are only as reliable as the
underlying model and the data it was trained on (see
`model_documentation.md` for limitations).

## Why a Probability Is Not a Guarantee
[DOMAIN KNOWLEDGE] A predicted probability reflects statistical patterns
learned from historical data. It does not account for:
- Information the model doesn't have access to (e.g., a satisfaction
  score, since this dataset doesn't include one)
- Future events that haven't happened yet (a customer could churn for
  reasons unrelated to any current feature)
- Model error — no model is perfectly accurate; some HIGH-risk customers
  will not churn, and some LOW-risk customers will.

Language like "the model estimates," "is likely to," or "the model flags
this customer as" is more accurate than "this customer will churn."

## How Businesses Can Use Risk Categories
[DOMAIN KNOWLEDGE]
- **Prioritization:** Focus limited retention resources on HIGH-risk
  customers first, especially when they also represent high value
  (`monthly_spend`).
- **Segmented messaging:** Different risk tiers can receive different
  outreach intensity (e.g., light nudges for MEDIUM, proactive outreach for
  HIGH).
- **Monitoring:** MEDIUM-risk customers can be tracked over time to see if
  they trend toward HIGH or back toward LOW.

## Appropriate Actions by Risk Level
[DOMAIN KNOWLEDGE — suggestions, not guaranteed outcomes; see
`retention_strategies.md` for a fuller playbook]

| Risk Level | Suggested Action Emphasis |
|---|---|
| LOW | Standard engagement; no urgent action required. |
| MEDIUM | Light-touch re-engagement; monitor for movement toward HIGH. |
| HIGH | Prioritized retention outreach; consider service recovery if support signals are present. |

These are general suggestions, not confirmed, tested retention outcomes for
this specific business.
