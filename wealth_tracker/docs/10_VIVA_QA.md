# 10. Viva Voce Examination Questions & Answers

This document prepares the student for common academic viva questions, technical evaluations, and project defense panels.

---

### Q1: What is the primary objective of your project?
**Answer:**
The objective of the **Smart Wealth Tracker and Budget Planner** is to provide an end-to-end personal finance management platform that pairs traditional income, expense, and budget tracking with practical machine learning. It solves the problem of manual tracking fatigue and financial blindness by automatically categorizing transactions using NLP, forecasting next month's spending burn rate using time-series linear regression, and helping users accomplish goal-based savings.

---

### Q2: Why did you choose Django for the backend?
**Answer:**
Django follows the "batteries-included" philosophy, providing:
1. **Built-in Security:** Default protection against Cross-Site Scripting (XSS), Cross-Site Request Forgery (CSRF), and SQL injection through its Object-Relational Mapper (ORM).
2. **Robust Authentication:** Production-ready user session management and password hashing (PBKDF2 with SHA-256).
3. **Seamless Python Ecosystem Integration:** Direct in-process access to scientific computing and machine learning libraries like `scikit-learn`, `pandas`, and `numpy` without needing separate microservice network bridges.

---

### Q3: Why did you use MySQL instead of Django's default SQLite3?
**Answer:**
SQLite is a serverless, file-based database intended primarily for lightweight local development and single-threaded operations. Personal finance applications handle sensitive monetary transactions requiring strict ACID compliance, concurrent read/write transactions, connection pooling, and multi-user scaling. MySQL 8.0 provides production-grade relational storage and transactional data integrity.

---

### Q4: How does the AI/ML layer work in your project?
**Answer:**
Our system incorporates four distinct AI/ML components:
1. **Auto Expense Categorization (NLP):** Uses `CountVectorizer` and a `MultinomialNB` (Multinomial Naive Bayes) classifier trained on 300+ Indian merchant memos (e.g. Swiggy, Uber, Electricity bill) to infer categories automatically.
2. **Spending Forecast:** Uses `LinearRegression` over historical monthly spending series to project next month's total expenditure and daily velocity.
3. **Anomaly Detection:** Employs Z-score deviation and Isolation Forest to flag unusually large transactions.
4. **Insights Engine:** A rule-based heuristic processor that turns statistical deltas into plain-language financial guidance.

---

### Q5: Can you explain the mathematics of Naive Bayes?
**Answer:**
Naive Bayes applies Bayes' Theorem with the assumption that words in a text are conditionally independent given the category:
$$P(\text{Category} \mid \text{Words}) = \frac{P(\text{Category}) \times \prod P(\text{Word}_i \mid \text{Category})}{P(\text{Words})}$$
We use Laplace smoothing ($\alpha = 1.0$) so that zero-frequency words never cause the total probability to become zero. The category with the highest posterior probability ($argmax$) is selected as the prediction.

---

### Q6: Why Linear Regression for forecasting instead of Deep Learning (LSTM) or ARIMA?
**Answer:**
1. **Data Availability:** Typical personal finance users have 6 to 12 months of transactions. Deep learning models like LSTMs or complex statistical models like ARIMA require hundreds of data points to avoid severe overfitting.
2. **Explainability:** Linear regression gives a clear slope $\beta_1$ ($y = \beta_1 x + \beta_0$). A positive slope clearly demonstrates an accelerating burn rate, which is easy to visualize and explain to an examiner.
3. **Computational Efficiency:** Instant model fitting without requiring GPU resources.

---

### Q7: How do you ensure Data Privacy between different users?
**Answer:**
We enforce strict multi-tenant data isolation:
1. Every model (`Transaction`, `Category`, `Budget`, `SavingsGoal`, `Asset`) has a `ForeignKey` pointing to `django.contrib.auth.models.User`.
2. Every database query in our views and services explicitly filters by `request.user` (e.g., `Transaction.objects.filter(user=request.user)`).
3. Primary key lookups use `get_object_or_404(Model, pk=pk, user=request.user)`, preventing any user from accessing another user's data by tampering with URLs.

---

### Q8: Why did you use `DecimalField` instead of `FloatField` for money?
**Answer:**
In Python and computer systems generally, `float` uses IEEE 754 binary floating-point representation, which cannot accurately represent certain decimal fractions (e.g., $0.1 + 0.2 = 0.30000000000000004$). In financial applications, this leads to cumulative rounding errors. Django's `DecimalField` uses Python's `decimal.Decimal` fixed-point arithmetic, ensuring exact monetary accounting down to the paisa.

---

### Q9: How are the charts rendered?
**Answer:**
Charts are rendered client-side in the user's browser using **Chart.js** via HTML5 Canvas. Django computes the numerical aggregations using SQL (`Sum`, `TruncMonth`), passes the arrays as JSON (`pie_labels`, `pie_data`, `bar_income`, `bar_expense`), and Chart.js draws interactive, responsive donut and bar charts with hover tooltips.

---

### Q10: How does the Savings Goal Tracker calculate progress?
**Answer:**
Each savings goal stores a `target_amount`, `saved_amount`, and `deadline`. The system calculates:
$$\text{Progress \%} = \left(\frac{\text{Saved Amount}}{\text{Target Amount}}\right) \times 100$$
$$\text{Remaining Balance} = \text{Target Amount} - \text{Saved Amount}$$
$$\text{Days Left} = \text{Deadline Date} - \text{Current Date}$$
$$\text{Required Monthly Saving} = \frac{\text{Remaining Balance}}{\lceil \text{Days Left} / 30 \rceil}$$

---

### Q11: What were the major technical challenges you faced and how did you resolve them?
**Answer:**
1. **Django and MySQL Version Incompatibility:** Local MySQL was 8.0.40, while Django 6 requires MySQL 8.4+. We resolved this by explicitly pinning Django to `5.1.5`.
2. **Missing Root URL & Static Config:** Originally, visiting the root URL returned 404 and static files were unconfigured. We resolved this by defining a public landing page at `path('', ...)` with auto-redirection for authenticated sessions and properly configuring `STATICFILES_DIRS = [BASE_DIR / 'static']`.
3. **Empty Cold-Start for AI:** When a new user signs up, they have zero transactions. We resolved this by pre-training the Naive Bayes classifier on a seed corpus of 300+ Indian merchant names and dynamically merging the user's new transactions as they are entered.

---

### Q12: How does the Net Worth Module compute financial solvency and the Net Worth Trajectory?
**Answer:**
1. **Net Worth Equation:** $\text{Net Worth} = \sum \text{Assets} - \sum \text{Liabilities}$.
2. **Solvency Metric:** $\text{Debt-to-Asset Ratio} = \left(\frac{\text{Total Liabilities}}{\text{Total Assets}}\right) \times 100$. A ratio $< 20\%$ indicates strong health, while $> 50\%$ triggers a high-leverage advisory.
3. **Trajectory Simulation:** Takes the present Net Worth snapshot and back-projects 6-month historical values by subtracting subsequent months' net cash flows ($\text{Monthly Income} - \text{Monthly Expenses}$).

---

### Q13: How does your Anomaly Detection Engine identify unusual spending transactions?
**Answer:**
We combine category-scoped statistical Z-scores with `IsolationForest` from `scikit-learn`:
$$Z = \frac{\text{Amount} - \mu_{\text{category}}}{\sigma_{\text{category}}}$$
Transactions where $Z > 2.0$ (exceeding 2 standard deviations above the category mean) are flagged as statistical outliers. The UI highlights them with an amber `Unusual Spend` badge and provides plain-language justification on the AI Hub (e.g. *"₹18,500 is 4.2x higher than your average Food spending"*).

---

### Q14: How does the AI Budget Recommendation Engine work?
**Answer:**
The engine analyzes the user's trailing 3-month spending velocity per category. It computes:
$$\text{Recommended Limit} = \text{round}\left(\text{3-Month Trailing Average} \times 1.05, -2\right)$$
The 5% buffer accommodates normal fluctuations while providing a realistic spending ceiling rounded to the nearest ₹100. Users can click "Apply Budget" to establish or adjust their monthly budget directly.

---

### Q15: How do you persist machine learning models in Django and avoid retraining on every request?
**Answer:**
We serialize trained models (`MultinomialNB` and `CountVectorizer`) using Python's `joblib` into the `ml_models/` directory via a custom Django management command:
```bash
python manage.py train_ml_models
```
At runtime, `predict_category` checks if serialized `.joblib` files exist on disk and loads them into memory instantly. If model artifacts are missing, the system automatically falls back to in-memory training on the seed dataset.

---

### Q16: How does the CSV Bank Statement Importer work?
**Answer:**
The importer accepts standard CSV exports from banks or fintech apps. It uses Python's `csv` module to inspect header rows, identifying columns like `Date`, `Amount`, `Description`, and `Type` through case-insensitive pattern matching. For transactions missing a category tag, the importer automatically invokes our Naive Bayes NLP pipeline to classify the transaction on the fly.

