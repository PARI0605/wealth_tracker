# 08. Architectural Decisions Log (ADR) & Viva Justifications

This document logs critical architectural, technical, and algorithmic decisions made in the project, explaining the alternatives considered and why this path was chosen (useful for viva defenses).

---

## Decision 1: Pinning Django to 5.1.5 instead of Django 6.0+
- **Context:** Django 6.0 enforces a strict prerequisite of MySQL 8.4 LTS or higher. The local workstation runs MySQL 8.0.40. Attempting to run Django 6 results in `django.db.utils.NotSupportedError: MySQL 8.4 or later is required`.
- **Decision:** Explicitly pin Django to version `5.1.5` in the virtual environment.
- **Viva Defense:** *"Django 5.1.5 provides full support for modern async features, enhanced ModelForm widgets, and modern security while maintaining full compatibility with the widely deployed enterprise MySQL 8.0 release series without requiring an invasive database server upgrade."*

---

## Decision 2: MySQL 8.0 Database over SQLite3
- **Context:** Django ships with SQLite3 by default. Academic projects often settle for SQLite.
- **Decision:** Use MySQL 8.0 (`wealth_tracker_db`) via `mysqlclient`.
- **Viva Defense:** *"Personal finance applications handle sensitive monetary transactions requiring strict ACID compliance, multi-user concurrency, row-level locking, and foreign key referential integrity that a server-based RDBMS like MySQL provides over file-based SQLite."*

---

## Decision 3: Multinomial Naive Bayes for Transaction Categorization
- **Alternatives Considered:** Deep Learning (BERT, RoBERTa), Large Language Model APIs (OpenAI / Gemini API), Rule-based regex.
- **Decision:** Implement scikit-learn's `MultinomialNB` paired with `CountVectorizer`.
- **Viva Defense:**
  1. *Sub-millisecond latency (< 5ms):* Live as-you-type categorization cannot afford the 500ms+ network round-trip of external cloud LLM APIs.
  2. *Data Privacy:* Financial transaction memos are processed 100% locally on the host server without transmitting user banking notes to third-party APIs.
  3. *Academic Rigor & Explainability:* Naive Bayes is an established probability theorem ($P(C \mid D) \propto P(C) \prod P(w_i \mid C)$). The decision boundaries and conditional word likelihoods can be mathematically derived and defended on a whiteboard during evaluation.

---

## Decision 4: Linear Regression (OLS) for Monthly Expense Prediction
- **Alternatives Considered:** ARIMA, SARIMA, LSTM Recurrent Neural Networks, Exponential Smoothing.
- **Decision:** Fit Ordinary Least Squares (OLS) Linear Regression over monthly aggregate spending series, supplemented by trailing daily velocity burn rates.
- **Viva Defense:**
  1. *Sample Size Reality:* A typical user tracks money for 3 to 12 months. ARIMA models require 50+ data points to reliably differentiate seasonal differencing and auto-regressive lags. Fitting ARIMA on 6 points leads to severe overfitting.
  2. *Interpretability:* Linear regression produces a tangible slope $\beta_1$ indicating whether the user's spending trajectory is accelerating or contracting.

---

## Decision 5: Separation of Concerns (Fat-Service / Thin-View)
- **Context:** Default Django beginner tutorials often dump all calculation logic inside `views.py`, making views 500+ lines long and difficult to test or explain.
- **Decision:** Introduce a dedicated `tracker/services/` layer (`dashboard_service.py`, `budget_service.py`, `goal_service.py`).
- **Viva Defense:** *"Views only handle HTTP protocol concerns (request/response/forms). Business formulas—such as computing budget consumption, daily spending velocity, and net worth—live in decoupled Python service modules that can be tested independently without mocking HTTP request objects."*

---

## Decision 6: Using `DecimalField` for Currency Values
- **Context:** Python's standard `float` type uses binary floating-point representation, causing representation discrepancies (e.g. `0.1 + 0.2 = 0.30000000000000004`).
- **Decision:** Use Django's `DecimalField(max_digits=10, decimal_places=2)` and Python's `decimal.Decimal` module across all monetary fields.
- **Viva Defense:** *"Financial applications must never use floating-point types due to precision loss during additions and subtractions. Decimal ensures fixed-point arithmetic exact down to the last paisa."*

---

## Decision 7: Chart.js for Client-Side Visualization over Matplotlib Images
- **Alternatives Considered:** Server-side Matplotlib PNG generation, D3.js.
- **Decision:** Use Chart.js loaded via CDN.
- **Viva Defense:** *"Matplotlib renders static bitmap images that cause server disk I/O bottlenecks and lack mobile responsiveness. Chart.js leverages HTML5 Canvas to provide responsive, interactive charts with animated hover tooltips and dynamic resizing directly in the client's browser."*
