# Model Documentation — Churn Prediction Model

## What This Document Covers
The machine learning model used to predict churn probability, its
preprocessing pipeline, and its limitations.

## Current Model
[MODEL FACT] The deployed model is a **Logistic Regression** classifier.

[DATASET FACT — from the project brief] The broader assignment scope calls
for training and comparing at least two different models; Logistic
Regression is documented here as the model currently specified for the
deployed application. If a second model is trained and compared, this
document should be updated with both, along with the comparison rationale
— that comparison has not been supplied yet, so it is not documented here.

## Why Preprocessing Is Required
[DOMAIN KNOWLEDGE] Logistic Regression, like most classical ML algorithms,
requires numerical input and is sensitive to feature scale. Raw customer
data mixes categorical fields (`gender`, `city`), numerical fields on very
different scales (`age` vs. `monthly_spend`), and potentially missing
values — all of which must be handled consistently before training.

## Numerical Feature Processing
[MODEL FACT] The pipeline includes numerical imputation and numerical
scaling.
- **Imputation:** [DOMAIN KNOWLEDGE] Fills in missing numerical values
  (e.g., a missing `monthly_spend`) using a consistent strategy (commonly
  mean or median) so the model can process every row without dropping data.
  The exact imputation strategy used (mean, median, etc.) has not been
  supplied.
- **Scaling:** [DOMAIN KNOWLEDGE] Rescales numerical features (e.g.,
  `age`, `tenure_months`, `monthly_spend`, `orders_count`,
  `support_tickets`) onto comparable ranges. This matters for Logistic
  Regression specifically because its coefficients are sensitive to the
  scale of each input — without scaling, a feature like `monthly_spend`
  (larger raw values) could dominate a feature like `orders_count` purely
  due to scale, not true predictive strength.

## Categorical Feature Processing
[MODEL FACT] The pipeline includes categorical imputation, one-hot
encoding, and handling of unknown categorical values.
- **Categorical imputation:** [DOMAIN KNOWLEDGE] Fills missing categorical
  values (e.g., a missing `city`) with a placeholder or most-frequent
  category, depending on strategy — exact strategy not supplied.
- **One-hot encoding:** [DOMAIN KNOWLEDGE] Converts categorical fields like
  `gender` and `city` into binary indicator columns (e.g., `city_Mumbai`,
  `city_Delhi`), since Logistic Regression requires numerical input and
  cannot directly use text categories.
- **Handling unknown categorical values:** [DOMAIN KNOWLEDGE] Ensures that
  if a new customer has a category value not seen during training (e.g., a
  new city), the pipeline doesn't fail — typically by encoding it as "all
  zeros" across the known one-hot columns or a dedicated "unknown" bucket.

## Logistic Regression
[DOMAIN KNOWLEDGE] Logistic Regression models the probability of the
positive class (`churn = 1`) as a function of a weighted, linear
combination of the input features, passed through a sigmoid function that
maps the result into a 0–1 probability range. Each feature has an
associated coefficient (weight) learned during training; the sign and
magnitude of a coefficient indicate the direction and strength of that
feature's linear relationship with churn, holding other features constant.

## Probability Prediction and Classification
[MODEL FACT] The model outputs a churn probability (e.g., `0.87` as in the
project's example API response). This probability is then mapped to a risk
category (LOW/MEDIUM/HIGH) — see `risk_levels.md` for how, and for the
important caveat that exact thresholds have not been supplied.

## Class Imbalance Handling
[MODEL FACT — NOT SUPPLIED] Whether the training process applied any
class-imbalance handling (e.g., class weighting, oversampling, undersampling)
has not been provided. Do not assume a specific technique was used; if
asked, state that this has not been documented.

## Model Limitations
[DOMAIN KNOWLEDGE]
- Logistic Regression assumes a roughly linear relationship (in log-odds
  space) between features and the outcome; it may underperform on complex,
  non-linear patterns compared to tree-based or ensemble models.
- It reflects patterns in historical training data; if customer behavior
  shifts over time, the model can become stale without retraining.
- It does not account for information outside the supplied features (e.g.,
  no satisfaction, acquisition-channel, or product-detail fields — see
  `dataset_overview.md`).
- No accuracy, precision, recall, F1, or ROC-AUC figures have been supplied
  for this project's trained model — none should be assumed, quoted, or
  invented until explicitly provided.

## Why Model Probability Should Not Automatically Be Interpreted as Certainty
[DOMAIN KNOWLEDGE] A probability output is the model's best statistical
estimate given the features it was trained on — not a guarantee of future
behavior. It carries model error, is limited by the features available, and
can be affected by data drift. See `risk_levels.md` for how this should be
communicated to end users.
