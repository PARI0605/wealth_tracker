# 06. Machine Learning Design & Algorithms: Smart Wealth Tracker

This document details all Artificial Intelligence and Machine Learning models integrated into the Smart Wealth Tracker, including algorithmic formulations, training datasets, evaluation metrics, pipeline architecture, and viva defense explanations.

---

## 1. Overview of AI/ML Capabilities

| ML Capability | Algorithm | Primary Libraries | Purpose | Status |
| :--- | :--- | :--- | :--- | :---: |
| **1. Auto Expense Categorization** | Multinomial Naive Bayes (`MultinomialNB`) + `CountVectorizer` | `scikit-learn` | Real-time classification of transaction memos/merchant names into categories. | **Implemented** |
| **2. Expense Prediction (Forecasting)** | Ordinary Least Squares Linear Regression (`LinearRegression`) | `scikit-learn`, `pandas` | Projects next month's spending burn rate based on historical monthly series. | **Implemented** |
| **3. Anomaly Outlier Detection** | Isolation Forest (`IsolationForest`) / Z-Score | `scikit-learn`, `scipy` | Identifies unusually high or irregular transactions to warn against fraud/overspending. | **Planned (Phase 5)** |
| **4. AI Spending Insights & Advisory** | Statistical Delta Heuristics & Velocity Engine | `pandas`, `numpy` | Translates numerical trends into plain-language actionable advice. | **Implemented (Refining)**|
| **5. Budget Recommender** | 3-Month Moving Average Velocity | `pandas` | Recommends realistic spending limits per category based on rolling averages. | **Planned (Phase 5)** |

---

## 2. Feature 1: Auto Expense Categorization (NLP)

### 2.1 Problem Formulation
Given an unstructured, short text string $D$ (e.g., `"Swiggy order biryani"`, `"Uber ride to airport"`, `"Bescom electricity bill"`), assign the most probable category label $C_k \in \{\text{Food}, \text{Transportation}, \text{Shopping}, \text{Bills}, \text{Entertainment}, \text{Health}, \text{Salary}, \dots\}$.

### 2.2 Mathematical Formulation (Multinomial Naive Bayes)
By Bayes' Theorem:
$$P(C_k \mid D) = \frac{P(C_k) \cdot P(D \mid C_k)}{P(D)}$$

Assuming conditional independence of words $w_1, w_2, \dots, w_n$ given category $C_k$:
$$P(C_k \mid w_1, \dots, w_n) \propto P(C_k) \prod_{i=1}^n P(w_i \mid C_k)$$

With Laplace smoothing ($\alpha = 1.0$):
$$P(w_i \mid C_k) = \frac{N_{k, i} + \alpha}{N_k + \alpha \cdot |V|}$$
Where:
- $N_{k, i}$ = count of word $w_i$ in category $C_k$.
- $N_k$ = total words in category $C_k$.
- $|V|$ = vocabulary size.

### 2.3 Training Dataset
The model is seeded with **300+ Indian-context merchant descriptions**:
- **Food:** Zomato, Swiggy, Starbucks, Dominos, McDonald's, Blinkit, Zepto, Dmart, Kirana, Haldirams, Chai Point.
- **Transportation:** Uber, Ola, Rapido, Metro recharge, DMRC, Indian Oil, HPCL petrol, IRCTC railway, IndiGo, Fastag.
- **Shopping:** Amazon, Flipkart, Myntra, Zara, H&M, Nykaa, Croma, Reliance Digital.
- **Bills & Utilities:** Bescom, Tata Power, Jio recharge, Airtel bill, piped gas, municipal water.
- **Entertainment:** Netflix, Spotify, BookMyShow, PVR cinemas, Prime Video, Hotstar.
- **Health:** Apollo Pharmacy, Practo, Netmeds, 1mg, diagnostic lab.
- **Salary / Income:** Monthly salary credit, freelance payout, interest credit, dividend.

### 2.4 User Adaptation & Retraining
When the user records or corrects a transaction, their specific descriptions are merged with the seed corpus and the classifier is retrained on demand or via `python manage.py train_ml_models`.

---

## 3. Feature 2: Expense Prediction & Forecasting (Time Series)

### 3.1 Problem Formulation
Given a sequence of historical monthly spending totals $Y = [y_1, y_2, \dots, y_m]$ across elapsed months $X = [1, 2, \dots, m]$, predict the expected expenditure $y_{m+1}$ for the upcoming calendar month.

### 3.2 Algorithm: Linear Regression (OLS)
The model fits a linear trajectory:
$$\hat{y} = \beta_0 + \beta_1 x$$

Where the parameters are computed via Ordinary Least Squares:
$$\beta_1 = \frac{\sum_{i=1}^m (x_i - \bar{x})(y_i - \bar{y})}{\sum_{i=1}^m (x_i - \bar{x})^2}, \quad \beta_0 = \bar{y} - \beta_1 \bar{x}$$

### 3.3 Daily Velocity & Month-End Projection
Within the active current month of $N$ total calendar days, on elapsed day $d$:
$$\text{Daily Burn Velocity} = \frac{\text{Spent to Date}}{d}$$
$$\text{Projected Month-End Spend} = \text{Daily Burn Velocity} \times N$$

If $\text{Projected Month-End Spend} > \text{Active Monthly Budget}$, the system triggers a **Budget Overrun Risk** alert.

### 3.4 Fallback Strategy
When a new user has fewer than 2 completed historical months, the system falls back to the trailing 30-day moving average to avoid zero-division errors.

---

## 4. Feature 3: Anomaly Detection (Outlier Flagging)

### 4.1 Objective
Flag individual transactions whose magnitude is statistically deviant compared to typical transactions within that specific category.

### 4.2 Algorithms:
1. **Z-Score Method (Parametric):**
   $$Z = \frac{x - \mu_{\text{category}}}{\sigma_{\text{category}}}$$
   If $Z > 2.5$, the transaction is marked with an **Anomaly Flag** (potential accidental double-charge or excessive impulse purchase).
2. **Isolation Forest (Non-Parametric):**
   Constructs an ensemble of isolation trees. Anomalies have shorter path lengths $E(h(x))$ from the root since outliers are isolated in fewer partitions.

---

## 5. Model Serialization & Storage
- Trained models are serialized using `joblib` into `wealthtracker/ml_models/`:
  - `category_model.joblib`: Trained `MultinomialNB` instance.
  - `vectorizer.joblib`: Trained `CountVectorizer` vocabulary dictionary.
- Training Command:
  ```bash
  python manage.py train_ml_models
  ```

---

## 6. Viva Defense: Why These Algorithms?
1. **Why Naive Bayes for Categorization over Deep Learning (BERT/LSTM)?**
   - Naive Bayes executes inference in **sub-millisecond (< 5ms)** time on CPU without needing heavy GPU instances.
   - Requires small training samples (~300 records) to achieve high accuracy on domain-specific keyword tokens.
   - Highly explainable: conditional log-probabilities can be directly inspected and defended in an academic evaluation.
2. **Why Linear Regression for Spending Forecasts over ARIMA/Prophet?**
   - Personal finances for a typical student/family generally cover 6 to 12 months of history; ARIMA requires 50+ observations to model seasonal differencing reliably.
   - Linear regression clearly exposes the trend slope $\beta_1$ (positive indicates spending expansion; negative indicates spending contraction).
