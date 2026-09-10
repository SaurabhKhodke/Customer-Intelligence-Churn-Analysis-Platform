# Feature Dictionary — Customer Intelligence / Churn Prediction

## What This Document Covers
A comprehensive, per-feature reference for every field in the customer churn
dataset. Each feature section is self-contained so it can be retrieved and
understood independently by the RAG system. Exact field names from the
source schema are used throughout — do not rename them.

Features are grouped by category. A separate group at the end lists
**suggested derived features** that are not yet confirmed as part of the
implemented feature set.

---

## Group: Identifier

### Feature: `customer_id`
- **Human-readable name:** Customer ID
- **Data type:** Integer / string identifier
- **Category:** Identifier
- **Definition:** [DATASET FACT] A unique identifier assigned to each
  customer record.
- **Business meaning:** Used to look up a specific customer's structured
  data, prediction, and SHAP explanation.
- **Churn relevance:** None — it is an identifier, not a behavioral signal,
  and should never be used as a predictive feature.
- **Typical interpretation:** N/A
- **Risk interpretation:** Not applicable.
- **Example:** `customer_id = 10432`
- **Caveats:** Should be excluded from model training features; retained only
  for lookup/joins between SQL, ML output, and SHAP output.
- **Raw or derived:** Raw.

---

## Group: Customer Demographics

### Feature: `age`
- **Human-readable name:** Age
- **Data type:** Numerical (integer, years)
- **Category:** Customer demographics
- **Definition:** [DATASET FACT] The customer's age in years.
- **Business meaning:** [DOMAIN KNOWLEDGE] Demographic context that can help
  segment customers for retention messaging or product targeting.
- **Churn relevance:** [DOMAIN KNOWLEDGE] Age alone is not a strong,
  universal churn driver; any relationship between age and churn is
  context-dependent and should be treated as **context-dependent risk**
  unless dataset evidence says otherwise.
- **Typical interpretation:** Used mainly for segmentation, not as a direct
  churn cause.
- **Risk interpretation:** Context-dependent — no fixed direction assumed.
- **Example:** `age = 34`
- **Caveats:** Do not assume age brackets correlate with churn without
  supporting evidence from EDA/model results.
- **Raw or derived:** Raw.

### Feature: `gender`
- **Human-readable name:** Gender
- **Data type:** Categorical
- **Category:** Customer demographics
- **Definition:** [DATASET FACT] The customer's recorded gender.
- **Business meaning:** [DOMAIN KNOWLEDGE] Can be used for fairness checks
  and segment-level reporting.
- **Churn relevance:** [DOMAIN KNOWLEDGE] No universal relationship to churn
  should be assumed; context-dependent risk only.
- **Typical interpretation:** Segmentation attribute.
- **Risk interpretation:** Context-dependent.
- **Example:** `gender = "Female"`
- **Caveats:** One-hot encoded for modeling; watch for class imbalance and
  fairness/bias implications when this feature contributes to predictions.
- **Raw or derived:** Raw.

### Feature: `city`
- **Human-readable name:** City
- **Data type:** Categorical
- **Category:** Customer demographics / location
- **Definition:** [DATASET FACT] The city associated with the customer.
- **Business meaning:** [DOMAIN KNOWLEDGE] Enables location-based analysis,
  e.g., churn rate by city, and can proxy for regional service quality,
  local competition, or delivery/logistics differences.
- **Churn relevance:** [DOMAIN KNOWLEDGE] City-level churn differences can
  emerge from local operational factors (e.g., delivery times, regional
  support quality). Any specific "City X has higher churn" claim must come
  from actual SQL/EDA output, not be assumed here.
- **Typical interpretation:** Used for segment-level churn-rate comparisons.
- **Risk interpretation:** Context-dependent — varies by city and must be
  backed by real aggregate data (see `sql/queries.sql` — churn rate by city).
- **Example:** `city = "Mumbai"`
- **Caveats:** High-cardinality categorical field; one-hot encoding may
  produce many columns. Sparse cities may have unreliable churn-rate
  estimates due to small sample size.
- **Raw or derived:** Raw.

---

## Group: Subscription / Account Information

### Feature: `tenure_months`
- **Human-readable name:** Tenure (Months)
- **Data type:** Numerical (integer, months)
- **Category:** Subscription / account information
- **Definition:** [DATASET FACT] The number of months the customer has held
  an active account/relationship with the business.
- **Business meaning:** [DOMAIN KNOWLEDGE] Indicates how established the
  customer relationship is. Longer tenure generally reflects a customer who
  has stayed engaged over time.
- **Churn relevance:** [DOMAIN KNOWLEDGE] Short tenure can be associated with
  higher churn risk (new customers who haven't built a habit yet — often
  called "early-life churn"). Long tenure does not guarantee retention, but
  can act as a stabilizing signal. Higher values may indicate **less risk**,
  though this is context-dependent and should be confirmed against actual
  model/SHAP behavior.
- **Typical interpretation:** Used both as a standalone feature and as the
  denominator for derived rate features (e.g., orders per month).
- **Risk interpretation:** Higher tenure may indicate lower risk
  (context-dependent; not confirmed by supplied evidence).
- **Example:** `tenure_months = 18`
- **Caveats:** A very short tenure paired with a support ticket can look
  different in risk terms than a long tenure with the same ticket — see
  `churn_signal_interpretation.md` for combined signals.
- **Raw or derived:** Raw.

---

## Group: Purchase / Engagement Behavior

### Feature: `orders_count`
- **Human-readable name:** Orders Count
- **Data type:** Numerical (integer)
- **Category:** Purchase behavior / engagement
- **Definition:** [DATASET FACT] The total number of orders placed by the
  customer.
- **Business meaning:** [DOMAIN KNOWLEDGE] A core measure of customer
  engagement and purchase frequency over the customer's history.
- **Churn relevance:** [DOMAIN KNOWLEDGE] Low order counts, especially
  relative to tenure, can be associated with disengagement and elevated
  churn risk. Higher values may indicate **less risk**, as a signal of an
  established purchase habit — context-dependent.
- **Typical interpretation:** Often interpreted alongside `tenure_months`
  (see `orders_per_month`, a suggested derived feature) rather than in
  isolation, since a low count for a brand-new customer means something
  different than a low count for a long-tenured one.
- **Risk interpretation:** Higher values may indicate less risk
  (context-dependent).
- **Example:** `orders_count = 42`
- **Caveats:** Interpreting this feature alone can be misleading — always
  consider tenure alongside it.
- **Raw or derived:** Raw.

### Feature: `last_order_date`
- **Human-readable name:** Last Order Date
- **Data type:** Date
- **Category:** Purchase behavior / recency
- **Definition:** [DATASET FACT] The date of the customer's most recent
  order.
- **Business meaning:** [DOMAIN KNOWLEDGE] The raw basis for measuring
  recency — how long it has been since the customer last engaged in a
  purchase.
- **Churn relevance:** [DOMAIN KNOWLEDGE] A `last_order_date` far in the past
  relative to today can be associated with disengagement and elevated churn
  risk. This is typically converted into a recency metric (days since last
  order) — see the suggested derived feature `recency_days` below.
- **Typical interpretation:** Rarely used directly by a model in raw date
  form; typically transformed into a recency measure.
- **Risk interpretation:** An older `last_order_date` (i.e., larger gap from
  today) may indicate higher risk — context-dependent, and only meaningful
  relative to a reference date.
- **Example:** `last_order_date = "2026-03-14"`
- **Caveats:** Must be interpreted relative to a consistent reference/"as of"
  date; comparing raw dates across different extraction times can be
  misleading.
- **Raw or derived:** Raw.

---

## Group: Spending Behavior

### Feature: `monthly_spend`
- **Human-readable name:** Monthly Spend
- **Data type:** Numerical (currency, e.g., USD/INR per month)
- **Category:** Spending behavior
- **Definition:** [DATASET FACT] A measure of the customer's spending on a
  monthly basis.
- **Business meaning:** [DOMAIN KNOWLEDGE] Indicates the customer's value to
  the business and their level of financial engagement.
- **Churn relevance:** [DOMAIN KNOWLEDGE] Relationship to churn is
  context-dependent: a sudden drop in spend can be a churn signal, while an
  already-low but stable spend may simply reflect a low-value segment rather
  than churn risk. Absolute spend level alone does not reliably indicate
  risk direction without a trend or comparison point.
- **Typical interpretation:** Most useful in combination with order activity
  and support signals rather than alone.
- **Risk interpretation:** Context-dependent.
- **Example:** `monthly_spend = 58.40`
- **Caveats:** Without a time series, a single spend figure can't show
  whether spend is rising, falling, or stable — a key limitation for churn
  interpretation (see `dataset_overview.md`).
- **Raw or derived:** Raw.

---

## Group: Support / Customer Service

### Feature: `support_tickets`
- **Human-readable name:** Support Tickets
- **Data type:** Numerical (integer, count)
- **Category:** Support / customer service
- **Definition:** [DATASET FACT] The number of customer support tickets
  raised by the customer.
- **Business meaning:** [DOMAIN KNOWLEDGE] A proxy for how much friction or
  difficulty the customer has experienced.
- **Churn relevance:** [DOMAIN KNOWLEDGE] A higher number of support tickets
  can be associated with increased churn risk, particularly when combined
  with low engagement or spend (see `churn_signal_interpretation.md`).
  Higher values may indicate **more risk** — context-dependent, since some
  tickets reflect resolved, positive-outcome interactions.
- **Typical interpretation:** Best interpreted alongside resolution outcome
  or satisfaction data if available; on its own it only measures volume of
  contact, not sentiment.
- **Risk interpretation:** Higher values may indicate more risk
  (context-dependent; ticket volume ≠ dissatisfaction by itself).
- **Example:** `support_tickets = 5`
- **Caveats:** This dataset does not capture ticket resolution status,
  sentiment, or category — do not infer "the customer is unhappy" from
  ticket count alone (see `customer_explanation_guidelines.md`).
- **Raw or derived:** Raw.

---

## Group: Target Variable

### Feature: `churn`
- **Human-readable name:** Churn (Target Label)
- **Data type:** Binary (0/1)
- **Category:** Target / outcome
- **Definition:** [DATASET FACT] Indicates whether the customer churned
  (`1`) or did not churn (`0`) in the observed period.
- **Business meaning:** The outcome the entire platform is built to predict
  and explain.
- **Churn relevance:** This *is* the churn label — not a predictor of
  itself.
- **Typical interpretation:** Used as the training label; the model outputs
  a predicted probability of `churn = 1` for new/unseen customers.
- **Risk interpretation:** Not applicable — this is the ground-truth
  outcome, not a risk-level input.
- **Example:** `churn = 1`
- **Caveats:** The exact operational rule used to assign this label (e.g.,
  inactivity threshold, cancellation event) has not been supplied — do not
  invent one.
- **Raw or derived:** Raw (label).

---

## Group: Suggested Derived Features (Not Yet Confirmed)

[DOMAIN KNOWLEDGE — SUGGESTED, NOT A CONFIRMED PART OF THE IMPLEMENTED FEATURE
SET] These are standard churn-modeling derived features that would plausibly
be engineered from the raw fields above. They are documented here so that,
*if and when they are implemented*, the RAG system already has grounded
definitions. They must not be treated as confirmed dataset facts until
implementation confirms them.

### Suggested Feature: `recency_days`
- **Human-readable name:** Recency (Days)
- **Definition:** Number of days between a reference "as of" date and
  `last_order_date`.
- **Churn relevance:** Higher values (longer time since last order) may
  indicate more risk — a common and well-supported pattern in churn
  modeling generally, though not yet confirmed for this specific model.
- **Raw or derived:** Derived, from `last_order_date`.

### Suggested Feature: `orders_per_month`
- **Human-readable name:** Orders per Month
- **Definition:** `orders_count / tenure_months` (with care taken to avoid
  division by zero for very new customers).
- **Churn relevance:** Lower values may indicate more risk (low purchase
  frequency relative to how long the customer has been active).
- **Raw or derived:** Derived, from `orders_count` and `tenure_months`.

### Suggested Feature: `support_tickets_per_month`
- **Human-readable name:** Support Tickets per Month
- **Definition:** `support_tickets / tenure_months`.
- **Churn relevance:** Higher values may indicate more risk (frequent
  friction relative to tenure).
- **Raw or derived:** Derived, from `support_tickets` and `tenure_months`.

**Not currently defined in the dataset at all** (flagged so the LLM does not
assume they exist): acquisition channel, subscription plan/tier,
satisfaction score, product category detail, payment method, contract type.
