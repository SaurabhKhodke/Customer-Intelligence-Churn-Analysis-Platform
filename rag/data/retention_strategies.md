# Retention Strategies — Playbook

## What This Document Covers
A signal-to-action mapping for customer retention, grounded in this
project's available fields. All content is [DOMAIN KNOWLEDGE] — general
retention practice — and every recommendation here is a **suggestion**, not
a guaranteed outcome. No recommendation in this document has been tested or
validated against this project's actual results.

---

### Signal: Long Gap Since Last Order (High Recency)
**Fields:** `last_order_date` (or suggested derived `recency_days`)
**Potential interpretation:** Customer has not purchased recently; may be
disengaging.
**Potential action:** Re-engagement campaign (email/push offer, "we miss
you" style outreach); consider a modest incentive to prompt a return visit.

### Signal: High Support Ticket Volume
**Fields:** `support_tickets`
**Potential interpretation:** Customer may be experiencing friction or
service problems.
**Potential action:** Proactive outreach to confirm recent issues were
resolved; service-recovery gesture if warranted; route to a senior support
agent for high-ticket-count customers.

### Signal: Low Order Frequency Relative to Tenure
**Fields:** `orders_count`, `tenure_months` (or suggested derived
`orders_per_month`)
**Potential interpretation:** Weak habit formation despite an established
account.
**Potential action:** Usage-education content, personalized product
recommendations, or a frequency-based incentive (e.g., "your next 3
orders").

### Signal: Short Tenure + Low Activity
**Fields:** `tenure_months` (low), `orders_count` (low)
**Potential interpretation:** Onboarding may not have successfully built a
habit yet.
**Potential action:** Structured onboarding follow-up, welcome-series
content, first-purchase-adjacent incentives to build momentum early.

### Signal: High Support Tickets + Low Spend/Orders
**Fields:** `support_tickets` (high), `monthly_spend`/`orders_count` (low)
**Potential interpretation:** Customer may be experiencing service problems
that are actively suppressing their engagement — a compounding risk
pattern.
**Potential action:** Prioritized support escalation / service recovery,
followed by a check-in once the issue is resolved.

### Signal: High Value, Low Engagement Frequency
**Fields:** `monthly_spend` (high), `orders_count` (low relative to tenure)
**Potential interpretation:** A valuable customer whose engagement is
thinner than their spend would suggest.
**Potential action:** Personalized, higher-touch outreach (e.g., account
manager style contact) given the customer's value; avoid generic mass
offers that may undervalue the relationship.

### Signal: Long Tenure + Declining Recent Activity
**Fields:** `tenure_months` (high), recent order activity (declining)
**Potential interpretation:** A previously loyal customer showing early
disengagement.
**Potential action:** Loyalty-acknowledging outreach ("we've valued having
you"), possibly paired with a win-back incentive that recognizes their
tenure specifically.

---

## Prioritization Guidance
[DOMAIN KNOWLEDGE] With limited retention resources, a common approach is
to prioritize by combining **risk level** (see `risk_levels.md`) with
**customer value** (`monthly_spend`), since HIGH-risk, high-value customers
represent the greatest potential loss if no action is taken. This is a
general prioritization heuristic, not a rule specific to this project's
validated results.

## Important Caveat
[DOMAIN KNOWLEDGE] Every action above is a **suggestion drawn from general
retention practice**, mapped to this project's available fields. None of
these actions have been tested for this business, and none are guaranteed
to reduce churn for any specific customer or segment. They should be
presented to end users as options to consider, not as proven remedies.
