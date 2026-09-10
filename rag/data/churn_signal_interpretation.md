# Churn Signal Interpretation — Combining Features

## What This Document Covers
How individual features in this dataset combine into more meaningful churn
signals, and why single-feature interpretation can be misleading. Every
example below is separated into:

- **A. General domain interpretation** — [DOMAIN KNOWLEDGE], standard
  churn-modeling reasoning that applies broadly, not proven for this
  project's data.
- **B. Findings actually supported by supplied project/model information**
  — currently empty, since no EDA results, correlations, or model outputs
  have been supplied for this project. This section exists so it can be
  filled in later without restructuring the document.

## Why Features Shouldn't Be Interpreted in Isolation
[DOMAIN KNOWLEDGE] A single feature value often has more than one plausible
explanation. For example, low `orders_count` could mean a disengaged
long-time customer (concerning) or a brand-new customer who simply hasn't
had time to order much yet (not concerning). Combining `orders_count` with
`tenure_months` resolves this ambiguity. This is why the SHAP explanation
for an individual customer (which reflects how the model weighed the *full*
feature combination) is more informative than reading any one feature value
alone — see `shap_explainability.md`.

---

## Example Signal Combinations (Using This Project's Fields)

### 1. Long Gap Since Last Order + Low Order Count
**Fields involved:** `last_order_date` (or the suggested derived
`recency_days`), `orders_count`

- **A. General domain interpretation:** [DOMAIN KNOWLEDGE] A customer who
  hasn't ordered recently *and* has a historically low order count shows
  both weak current engagement and weak historical engagement — generally a
  stronger disengagement signal than either alone.
- **B. Project-specific finding:** Not yet established — no supplied
  evidence.

### 2. High Support Ticket Volume + Low Spend/Orders
**Fields involved:** `support_tickets`, `monthly_spend`, `orders_count`

- **A. General domain interpretation:** [DOMAIN KNOWLEDGE] A customer who
  is raising support tickets while also spending or ordering less can
  suggest the customer is experiencing friction that is affecting their
  usage — a classically watched combination in churn analysis, since it
  pairs a "problem" signal with a "disengagement" signal.
- **B. Project-specific finding:** Not yet established.

### 3. Short Tenure + Low Activity
**Fields involved:** `tenure_months`, `orders_count`

- **A. General domain interpretation:** [DOMAIN KNOWLEDGE] New customers
  with low order counts can indicate onboarding/habit-formation failure —
  the customer hasn't yet found consistent value. This differs from the
  "declining loyalist" pattern (long tenure, low recent activity) and may
  call for a different retention response (see `retention_strategies.md`).
- **B. Project-specific finding:** Not yet established.

### 4. Long Tenure + Declining Recent Activity
**Fields involved:** `tenure_months` (high), recent order activity (low)

- **A. General domain interpretation:** [DOMAIN KNOWLEDGE] A previously
  loyal customer whose activity is dropping off can be a high-value save
  opportunity, since they have a demonstrated history of engagement (unlike
  a never-engaged new customer). Note: this dataset provides snapshot
  values rather than a time series, so "declining" activity cannot be
  directly measured without historical data — this pattern is currently
  only inferable, not measurable, in the available schema.
- **B. Project-specific finding:** Not yet established.

### 5. High Spend but Low Order Frequency
**Fields involved:** `monthly_spend` (high), `orders_count` (low relative
to tenure)

- **A. General domain interpretation:** [DOMAIN KNOWLEDGE] This can
  describe a high-value but infrequent buyer — a segment sometimes at risk
  because their engagement is thin even though their revenue contribution
  is significant (see `customer_behavior_patterns.md`,
  "high-value but disengaged customers").
- **B. Project-specific finding:** Not yet established.

---

## How to Use This Document
[DOMAIN KNOWLEDGE] When a user asks "why is this combination risky?", the
LLM should:
1. Explain the *general* reasoning (section A style), clearly framed as
   domain knowledge.
2. Check whether a project-specific finding (section B) exists for that
   combination; if not, say so rather than presenting general reasoning as
   a confirmed dataset result.
3. Where possible, ground the explanation in the specific customer's actual
   SQL data and SHAP values (see `customer_explanation_guidelines.md`)
   rather than only general patterns.
