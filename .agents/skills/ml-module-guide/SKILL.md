---
name: ml-module-guide
description: Guidelines for developing, training, evaluating, serializing, and explaining Machine Learning models in the Smart Wealth Tracker project.
---

# Machine Learning Module & Engineering Guide

## When to Use This Skill
Activate this skill whenever creating, modifying, training, evaluating, or explaining AI/ML algorithms in the project.

---

## 1. Directory & File Placement
- All ML algorithms, vectorizers, and inference functions must reside in `tracker/ml/` (or `tracker/ai.py`).
- Persisted serialized models must be stored with `joblib` in `wealthtracker/ml_models/`.
- Training seed dataset must live in `tracker/ml/data/seed_transactions.csv`.

---

## 2. Algorithm Standards & Explainability

### Feature 1: Naive Bayes NLP Categorizer
- **Algorithm:** `MultinomialNB` paired with `CountVectorizer(ngram_range=(1, 2), lowercase=True)`.
- **Requirements:**
  - Must return `(predicted_category_name, confidence_percentage, matched_category_obj)`.
  - Must handle cold-starts gracefully via seed dataset of 300+ Indian merchant memos.
  - User's recorded transactions must be dynamically folded into retraining.

### Feature 2: Linear Regression Spending Forecaster
- **Algorithm:** `LinearRegression()` from `sklearn.linear_model`.
- **Requirements:**
  - Aggregates spending by month using `pandas`.
  - Fits line $y = mx + c$ on month index sequence ($X = [1, 2, 3 \dots]$).
  - Calculates daily spending velocity and projected month-end burn rate.
  - Triggers budget overrun alert if projected total exceeds active monthly budget.
  - Fallback: Trailing 30-day moving average if fewer than 2 monthly data points exist.

### Feature 3: Anomaly Detection
- **Algorithm:** Z-score deviation ($Z > 2.5$) and/or `IsolationForest`.
- **Requirements:**
  - Evaluates transactions against historical category means $\mu$ and standard deviations $\sigma$.
  - Generates warning badge and alert for unusually large debit amounts.

---

## 3. Training & Serialization Command
Models must be trainable via Django management command:
```bash
python manage.py train_ml_models
```
Ensure models load with `joblib.load()` with automatic training fallback if model files are missing on disk.
