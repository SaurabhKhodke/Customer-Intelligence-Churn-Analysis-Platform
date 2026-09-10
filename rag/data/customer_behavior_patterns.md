# Customer Behavior Patterns

## What This Document Covers
Named, reusable behavior-pattern concepts that the LLM can use when
reasoning about a customer's combination of feature values. All patterns
here are [DOMAIN KNOWLEDGE] — general customer-analytics concepts — and are
**not** claimed to be statistically proven within this project's dataset
unless a future update adds supporting evidence.

Each pattern is described using this project's actual field names where
possible: `tenure_months`, `orders_count`, `monthly_spend`,
`support_tickets`, `last_order_date`.

---

### Dormant Customers
- **Characteristics:** Long gap since `last_order_date`; low recent
  `orders_count` activity.
- **Possible churn interpretation:** Weak current engagement; elevated risk
  if the gap is unusually long relative to the customer's own history or
  tenure.
- **Business significance:** May still be recoverable with the right
  prompt, but the longer the dormancy, the lower the typical win-back rate
  in general churn practice.
- **Possible retention approach:** Re-engagement campaign, incentive-based
  win-back offer.

### Highly Engaged Customers
- **Characteristics:** Frequent, recent orders; relatively high
  `orders_count` for their `tenure_months`.
- **Possible churn interpretation:** Generally lower near-term risk.
- **Business significance:** Strong retention baseline; good candidates for
  loyalty/referral programs.
- **Possible retention approach:** Reward and reinforce the existing
  habit rather than heavy discounting.

### Frequent Buyers
- **Characteristics:** High `orders_count` relative to `tenure_months`
  (i.e., high order frequency).
- **Possible churn interpretation:** Generally lower risk, though a sudden
  drop from a high baseline can be a meaningful negative signal — not
  measurable without historical/trend data in this dataset.
- **Business significance:** Often disproportionately valuable; worth
  monitoring for any deceleration.
- **Possible retention approach:** Maintain service quality; monitor for
  early signs of slowdown.

### Low-Frequency Buyers
- **Characteristics:** Low `orders_count` relative to `tenure_months`.
- **Possible churn interpretation:** Weak habit formation; can indicate
  elevated risk, particularly for longer-tenured customers.
- **Business significance:** May represent under-realized value if the
  product fit is right but engagement hasn't caught on.
- **Possible retention approach:** Targeted engagement nudges,
  product-usage education, or incentive to increase order frequency.

### High-Support Customers
- **Characteristics:** Elevated `support_tickets` count.
- **Possible churn interpretation:** Can indicate friction, though ticket
  volume alone doesn't reveal whether issues were resolved satisfactorily
  (not captured in this dataset).
- **Business significance:** A visible opportunity for direct intervention,
  since the customer has already engaged with support.
- **Possible retention approach:** Proactive follow-up, service recovery,
  ensure recent tickets were fully resolved.

### Dissatisfied Customers
- **Characteristics:** Would typically be identified via a satisfaction or
  sentiment field. **This dataset does not include one** — high
  `support_tickets` can be a partial proxy but should not be equated with
  "dissatisfied" on its own.
- **Possible churn interpretation:** Elevated risk, when actual
  satisfaction data confirms it.
- **Business significance:** High-priority for intervention when confirmed.
- **Possible retention approach:** Direct outreach, service recovery,
  explicit satisfaction check-in.
- **Caveat:** The LLM should not label a customer "dissatisfied" from
  `support_tickets` alone — see `customer_explanation_guidelines.md`.

### High-Value but Disengaged Customers
- **Characteristics:** High `monthly_spend` combined with low
  `orders_count`/order frequency.
- **Possible churn interpretation:** Engagement is thin relative to the
  revenue they represent — a segment often prioritized for retention
  despite looking "fine" on spend alone.
- **Business significance:** High potential revenue impact if lost.
- **Possible retention approach:** White-glove or personalized outreach,
  given their value.

### New Customers With Weak Engagement
- **Characteristics:** Short `tenure_months`, low `orders_count`.
- **Possible churn interpretation:** Onboarding/habit-formation risk rather
  than "declining loyalist" risk — a different pattern requiring a
  different response.
- **Business significance:** Early intervention can meaningfully shape
  long-term retention, since the relationship is still forming.
- **Possible retention approach:** Onboarding support, early-usage
  incentives, education on product value.

### Long-Tenure Customers With Declining Activity
- **Characteristics:** High `tenure_months`, but recent activity
  (`orders_count` relative to history, `last_order_date`) trailing off.
- **Possible churn interpretation:** A previously loyal customer becoming
  disengaged — often considered a high-priority save given their
  demonstrated history.
- **Business significance:** High switching cost for the business to
  replace an established relationship; often worth extra retention effort.
- **Possible retention approach:** Personalized re-engagement referencing
  their history/loyalty, rather than generic new-customer offers.

---

## Usage Note
[DOMAIN KNOWLEDGE] These patterns are reasoning aids for interpreting a
combination of feature values — not classifications the model itself
outputs. Whether a specific customer matches one of these patterns should
be checked against that customer's actual SQL data, not assumed. See
`customer_explanation_guidelines.md` for how to combine this domain
knowledge with real customer facts.
