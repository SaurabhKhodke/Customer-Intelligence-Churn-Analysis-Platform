# Churn Concepts — Domain Knowledge

## What This Document Covers
Foundational customer-churn theory, written to be directly applicable to
this project's feature set (`age`, `gender`, `city`, `tenure_months`,
`monthly_spend`, `orders_count`, `support_tickets`, `last_order_date`,
`churn`). All content here is [DOMAIN KNOWLEDGE] — general customer-churn
theory — unless explicitly marked as a dataset or model fact elsewhere.

## What Customer Churn Means
[DOMAIN KNOWLEDGE] Churn is the event of a customer ending their
relationship with a business — cancelling a subscription, stopping
purchases, or otherwise becoming inactive. In this project, churn is
captured as a binary label (`churn = 1` for churned customers).

## Why Customers Churn
[DOMAIN KNOWLEDGE] Common, general reasons customers churn include:
- Declining engagement or habit loss
- Poor service experiences or unresolved issues
- Better alternatives elsewhere (competitive pressure)
- Price sensitivity or perceived lack of value
- Life-stage or need changes (the product no longer fits their situation)
- Onboarding failure (never formed a habit in the first place)

None of these specific causes can be confirmed for this project's customers
without supporting evidence (e.g., a documented reason field, survey data,
or statistically supported patterns). The dataset itself does not include a
churn-reason field.

## Voluntary vs. Involuntary Churn
[DOMAIN KNOWLEDGE]
- **Voluntary churn:** The customer actively decides to leave (e.g.,
  cancels, stops ordering by choice).
- **Involuntary churn:** The customer leaves for reasons not tied to
  satisfaction (e.g., a failed payment method, relocation).

This dataset does not distinguish between the two — `churn` is a single
binary outcome. Any claim about *why* a customer churned should be
qualified as an interpretation, not a documented fact.

## Behavioral Indicator Categories
[DOMAIN KNOWLEDGE] Churn risk is usually read through a combination of
indicator categories rather than any single feature:

### Engagement Indicators
General activity level with the product/service. In this dataset,
`orders_count` and `last_order_date` are the closest available proxies.

### Purchase Indicators
Direct measures of buying behavior — `orders_count`, `monthly_spend`.

### Satisfaction Indicators
Direct measures of how happy a customer is (e.g., survey/NPS score). **Not
present in this dataset.** Do not infer satisfaction from spend or order
count alone.

### Support / Complaint Indicators
Volume and nature of customer service interactions. `support_tickets` is
the available proxy, though it captures volume only, not sentiment or
resolution outcome.

### Recency
How recently the customer engaged. `last_order_date` is the raw field;
`recency_days` (days since last order) is a common derived transformation
of it — see `feature_dictionary.md` for its (currently suggested, not
confirmed) definition.

### Frequency
How often the customer engages. `orders_count`, potentially normalized by
`tenure_months` into `orders_per_month`.

### Monetary / Spending Behavior
The customer's financial engagement. `monthly_spend` is the available
proxy.

### Tenure
How long the customer relationship has existed. `tenure_months` is the
direct field. New customers (short tenure) are often at elevated risk of
"early-life churn" because the habit hasn't formed yet; long-tenured
customers with declining activity can represent a different, "at-risk
loyalist" pattern.

### Subscription-Related Risk
[DOMAIN KNOWLEDGE] In subscription businesses generally, risk often spikes
around renewal/billing dates. This dataset does not include a subscription
plan or billing-cycle field, so this pattern cannot currently be evaluated
here.

### Acquisition-Channel Differences
[DOMAIN KNOWLEDGE] Customers acquired through different channels
(referral, paid ads, organic) often show different churn profiles. This
dataset does not include an acquisition-channel field.

## Early Warning Signals
[DOMAIN KNOWLEDGE] A single weak signal is rarely conclusive. Early warning
often comes from a **change or divergence** relative to a customer's own
baseline — e.g., a longer-than-usual gap since the last order, or a new
support ticket after a long ticket-free period — more than from an absolute
value. This dataset provides snapshot values (not historical time series),
which limits the ability to detect *change* directly; see
`dataset_overview.md` for this limitation.

## Combinations of Signals
[DOMAIN KNOWLEDGE] Individual features are usually weaker evidence than
combinations of features. See `churn_signal_interpretation.md` for
worked examples of how signals should be combined rather than read in
isolation.

## Association vs. Causation — An Important Distinction

**"Feature associated with churn"**
[DOMAIN KNOWLEDGE] Means the feature and churn tend to co-occur or
correlate in the data/model — e.g., customers with high `support_tickets`
counts are, in the observed data, more often labeled `churn = 1`. This is a
statistical/pattern-based relationship.

**"Feature causing churn"**
[DOMAIN KNOWLEDGE] Would mean the feature is a direct driver — that
changing it would change the churn outcome. Establishing causation requires
controlled experiments (e.g., A/B tests) or causal inference methods, not
just observational correlation or SHAP contribution values.

**Why this matters for this project:** SHAP values and model coefficients
describe how a feature contributes to a *prediction*, which reflects
learned association in the training data — not proven causation. The
system should always use language like "may indicate," "can be associated
with," or "is a signal of" rather than "causes," unless a causal study is
explicitly supplied. See `model_documentation.md` and
`shap_explainability.md` for how this applies to model outputs.
