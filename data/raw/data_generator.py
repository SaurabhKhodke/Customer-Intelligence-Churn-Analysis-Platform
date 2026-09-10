# ============================================================
# CELL 1 — CREATE REALISTIC SYNTHETIC CUSTOMER CHURN DATASET (v2)
# ============================================================
# Design goals (why this version is different from a "random with
# a target bolted on" generator):
#
#   1. Every variable that drives churn is either IN the final
#      dataset or DERIVABLE from it (recency <- last_order_date).
#      Nothing that predicts churn is hidden from the model.
#   2. Churn depends on several correlated, business-plausible
#      drivers + a bounded latent "noise" term, tuned so a
#      properly engineered model lands around ROC-AUC ~0.85-0.92 —
#      learnable, but not a trivial 0.99 giveaway.
#   3. One genuine interaction is baked in (support load matters
#      much more for new customers than tenured ones), so SHAP has
#      something real to surface for the explainability section.
#   4. Deliberate, logged data-quality issues are injected
#      (missing values, dupes, bad rows, inconsistent text) so the
#      "data cleaning" part of the assignment has real work to do.
# ============================================================

import numpy as np
import pandas as pd
from pathlib import Path

RANDOM_STATE = 42
N_CUSTOMERS = 100_000        # raise to 100_000 later if you want; generation is O(n)
REFERENCE_DATE = pd.Timestamp("2025-12-31")
INJECT_DATA_QUALITY_ISSUES = True   # set False for a "clean" run

rng = np.random.default_rng(RANDOM_STATE)

RAW_DIR = Path("../data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def z(x: np.ndarray) -> np.ndarray:
    return (x - x.mean()) / x.std()


# ------------------------------------------------------------
# 1. Identity & demographics
# ------------------------------------------------------------
customer_id = np.arange(100001, 100001 + N_CUSTOMERS)

age = np.clip(rng.normal(42, 13, N_CUSTOMERS), 18, 75).round().astype(int)

gender = rng.choice(["Male", "Female", "Other"], N_CUSTOMERS, p=[0.48, 0.49, 0.03])

cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad"]
city_probs = [0.17, 0.15, 0.14, 0.12, 0.11, 0.11, 0.10, 0.10]
city = rng.choice(cities, N_CUSTOMERS, p=city_probs)

channels = ["Organic", "Paid Ads", "Referral", "Social Media", "Email Campaign"]
channel_probs = [0.32, 0.24, 0.18, 0.16, 0.10]
acquisition_channel = rng.choice(channels, N_CUSTOMERS, p=channel_probs)

plans = ["Basic", "Standard", "Premium"]
plan_probs = [0.50, 0.35, 0.15]
subscription_plan = rng.choice(plans, N_CUSTOMERS, p=plan_probs)

payment_methods = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet"]
payment_probs = [0.34, 0.26, 0.20, 0.12, 0.08]
payment_method = rng.choice(payment_methods, N_CUSTOMERS, p=payment_probs)

# ------------------------------------------------------------
# 2. Tenure & signup date
# ------------------------------------------------------------
tenure_months = np.clip(rng.gamma(3.2, 8.5, N_CUSTOMERS), 1, 60).round().astype(int)
signup_jitter_days = rng.integers(0, 30, N_CUSTOMERS)
signup_date = REFERENCE_DATE - pd.to_timedelta(tenure_months * 30 + signup_jitter_days, unit="D")

# ------------------------------------------------------------
# 3. Orders, spend, discount usage (plan-aware, so plan isn't
#    just a decorative column)
# ------------------------------------------------------------
plan_order_factor = pd.Series(subscription_plan).map(
    {"Basic": 0.85, "Standard": 1.0, "Premium": 1.35}
).values
base_order_rate = np.clip((1.1 + 0.075 * tenure_months) * plan_order_factor, 0.3, None)
orders_count = np.maximum(rng.poisson(base_order_rate), 1)

plan_aov_mean = pd.Series(subscription_plan).map(
    {"Basic": 800, "Standard": 1200, "Premium": 2100}
).values
average_order_value = rng.lognormal(np.log(plan_aov_mean), 0.4)
customer_spending_factor = rng.lognormal(0, 0.3, N_CUSTOMERS)

monthly_spend = np.clip(
    orders_count * average_order_value * customer_spending_factor, 200, 40000
).round(2)

plan_alpha = pd.Series(subscription_plan).map({"Basic": 5.0, "Standard": 4.0, "Premium": 2.0}).values
plan_beta = pd.Series(subscription_plan).map({"Basic": 3.0, "Standard": 4.0, "Premium": 5.0}).values
discount_usage_rate = rng.beta(plan_alpha, plan_beta).round(3)

# ------------------------------------------------------------
# 4. Support tickets & satisfaction
# ------------------------------------------------------------
friction = rng.gamma(1.2, 0.5, N_CUSTOMERS)  # per-customer "how much friction do they generate"
support_lambda = 0.6 + 0.02 * orders_count + friction
support_tickets = np.clip(rng.poisson(support_lambda), 0, 20)

support_ratio = support_tickets / (orders_count + 1)
support_ratio_z = z(support_ratio)

satisfaction_score = np.clip(
    np.round(4.3 - 0.6 * support_ratio_z + rng.normal(0, 0.5, N_CUSTOMERS)), 1, 5
).astype(int)

# ------------------------------------------------------------
# 5. Recency / last order date
# ------------------------------------------------------------
recency = rng.gamma(2.6, 42, N_CUSTOMERS) + rng.normal(0, 15, N_CUSTOMERS)
recency = np.clip(recency, 1, 365).round().astype(int)
last_order_date = REFERENCE_DATE - pd.to_timedelta(recency, unit="D")

# ------------------------------------------------------------
# 6. Latent factors (unobserved loyalty / product-fit + a small
#    regional effect, so "churn rate by city" isn't perfectly flat)
# ------------------------------------------------------------
customer_health = rng.normal(0, 1, N_CUSTOMERS)
city_effect_lookup = dict(zip(cities, rng.normal(0, 0.12, len(cities))))
city_effect = pd.Series(city).map(city_effect_lookup).values

# ------------------------------------------------------------
# 7. Churn probability
# ------------------------------------------------------------
recency_z = z(recency)
tenure_z = z(tenure_months)
orders_z = z(orders_count)
spend_z = z(monthly_spend)
satisfaction_z = z(satisfaction_score)
discount_z = z(discount_usage_rate)

plan_effect = pd.Series(subscription_plan).map({"Basic": 0.30, "Standard": 0.0, "Premium": -0.45}).values
channel_effect = pd.Series(acquisition_channel).map(
    {"Organic": -0.10, "Referral": -0.30, "Social Media": 0.05, "Email Campaign": 0.05, "Paid Ads": 0.25}
).values

# genuine interaction: support friction hurts NEW customers far more than tenured ones
interaction_term = 0.30 * support_ratio_z * (-tenure_z)

churn_logit = (
    -1.55
    + 1.15 * recency_z
    + 0.55 * support_ratio_z
    - 0.45 * tenure_z
    - 0.35 * orders_z
    - 0.15 * spend_z
    - 0.30 * satisfaction_z
    + 0.15 * discount_z
    + plan_effect
    + channel_effect
    + city_effect
    + interaction_term
    - 0.45 * customer_health
)

churn_probability = 1 / (1 + np.exp(-churn_logit))
churn = (rng.random(N_CUSTOMERS) < churn_probability).astype(int)

# ------------------------------------------------------------
# 8. Assemble
# ------------------------------------------------------------
df = pd.DataFrame({
    "customer_id": customer_id,
    "age": age,
    "gender": gender,
    "city": city,
    "acquisition_channel": acquisition_channel,
    "subscription_plan": subscription_plan,
    "payment_method": payment_method,
    "signup_date": signup_date,
    "tenure_months": tenure_months,
    "orders_count": orders_count,
    "monthly_spend": monthly_spend,
    "discount_usage_rate": discount_usage_rate,
    "support_tickets": support_tickets,
    "satisfaction_score": satisfaction_score,
    "last_order_date": last_order_date,
    "churn": churn,
})

# ------------------------------------------------------------
# 9. Inject realistic data-quality issues (so "data cleaning" in
#    the assignment has real work to do — a perfectly clean
#    synthetic dataset can't demonstrate that skill)
# ------------------------------------------------------------
if INJECT_DATA_QUALITY_ISSUES:
    n = len(df)
    idx = rng.permutation(n)

    df.loc[idx[:int(0.015 * n)], "age"] = np.nan                      # 1.5% missing age
    df.loc[idx[int(0.015 * n):int(0.025 * n)], "gender"] = np.nan      # 1.0% missing gender
    df.loc[idx[int(0.025 * n):int(0.035 * n)], "city"] = np.nan        # 1.0% missing city
    df.loc[idx[int(0.035 * n):int(0.043 * n)], "monthly_spend"] = np.nan  # 0.8% missing spend

    lo_slice = idx[int(0.043 * n):int(0.053 * n)]
    pad_slice = idx[int(0.053 * n):int(0.063 * n)]
    df.loc[lo_slice, "city"] = df.loc[lo_slice, "city"].astype(str).str.lower()      # "mumbai"
    df.loc[pad_slice, "city"] = df.loc[pad_slice, "city"].astype(str) + "  "         # "Pune  "

    dup_rows = df.sample(max(int(0.005 * n), 1), random_state=RANDOM_STATE)
    df = pd.concat([df, dup_rows], ignore_index=True)                  # ~0.5% exact duplicates

    bad_idx = rng.choice(df.index, size=15, replace=False)
    df.loc[bad_idx[:5], "orders_count"] = -1        # impossible negative orders
    df.loc[bad_idx[5:10], "monthly_spend"] = 999999.0   # obvious entry-error outlier
    df.loc[bad_idx[10:], "age"] = 130                # impossible age

    inconsistent_idx = rng.choice(df.index, size=10, replace=False)
    df.loc[inconsistent_idx, "last_order_date"] = df.loc[inconsistent_idx, "signup_date"] - pd.Timedelta(days=5)
    # ^ last order before signup — a logical inconsistency worth catching in EDA

# ------------------------------------------------------------
# 10. Shuffle, save, verify
# ------------------------------------------------------------
df = df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)

output_path = RAW_DIR / "customer_churn_raw.csv"
df.to_csv(output_path, index=False)

print("=" * 70)
print("SYNTHETIC CUSTOMER CHURN DATASET CREATED")
print("=" * 70)
print(f"\nShape: {df.shape}")
print(f"\nChurn rate: {df['churn'].mean():.2%}")
miss = df.isnull().sum()
print(f"\nMissing values:\n{miss[miss > 0]}")
print(f"\nDuplicate rows: {df.duplicated().sum()}")
print(f"\nSaved to: {output_path.resolve()}")