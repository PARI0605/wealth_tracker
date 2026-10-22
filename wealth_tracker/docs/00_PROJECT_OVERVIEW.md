# 00. Project Overview: Smart Wealth Tracker and Budget Planner

## 1. Project Title
**Smart Wealth Tracker and Budget Planner using Python (Django) and MySQL**

---

## 2. Academic Identity & Project Context
- **Project Type:** College Minor Project (Academic).
- **Primary Requirement:** Code must be modular, thoroughly commented, well-documented, clean, and easily explainable by an undergraduate student during viva evaluations and demonstrations.
- **Mandatory Academic Rule:** Incorporate practical Artificial Intelligence and Machine Learning (AI/ML) concepts for automated classification, time-series spending forecasting, anomaly detection, and natural language financial insights.
- **Currency & Localization:** Indian Rupee (₹), formatted with Indian number grouping conventions (e.g., ₹1,00,000). Timezone: `Asia/Kolkata`.

---

## 3. Purpose & Problem Statement
### The Problem:
Most individuals and households manage their day-to-day income and expenditure through memory, paper notebooks, or disconnected spreadsheets. This manual approach leads to:
1. **Lack of Behavioral Insights:** People are unaware of what proportion of their income is consumed by discretionary categories (e.g., dining out, subscription creep, impulse shopping).
2. **Budget Overruns:** Budgets are either not set or monitored too late—often when bank balances are depleted.
3. **Poor Goal Savings:** Savings goals lack milestone tracking, deadline countdowns, and mathematical deposit recommendations.
4. **Manual Friction:** Categorizing transactions manually is tedious, leading to tracking abandonment.

### The Solution:
The **Smart Wealth Tracker and Budget Planner** computerizes financial management and integrates an intelligent AI/ML layer to:
- Auto-categorize merchant descriptions in real-time using Natural Language Processing (NLP: Naive Bayes / Logistic Regression).
- Forecast next month's spending burn rate using Linear Regression on historical time-series sequences.
- Provide automated anomaly detection and plain-language spending guidance.
- Track category budgets with visual progress indicators and milestone-driven savings goals.
- Calculate overall Net Worth through asset and liability tracking.

---

## 4. Objectives
1. **Financial Tracking:** Provide an intuitive ledger to record, edit, filter, search, import, and export income and expense transactions.
2. **Budget Optimization:** Enable category-wise monthly spending caps with live visual alerts before thresholds are breached.
3. **Goal-Oriented Wealth Accumulation:** Enable deadline-bound savings targets with progress rings and monthly required deposit calculations.
4. **Interactive Visual Analytics:** Render clear, responsive Chart.js visual charts (category donut breakdowns, 6-month comparative cash flow bars, and net worth trajectory).
5. **Applied Machine Learning:**
   - NLP-based transaction description classifier.
   - Time-series linear regression spending forecaster.
   - Isolation Forest / Z-score outlier anomaly detector.
   - Explainable rule-based insights and recommendations.

---

## 5. Fixed Technology Stack (Non-Negotiable)
| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Runtime** | Python 3.13 | Core programming language |
| **Web Framework** | Django 5.1.5 | Fixed & pinned (Django 6+ requires MySQL 8.4+, whereas local environment uses MySQL 8.0.40) |
| **Database** | MySQL 8.0.40 | Database: `wealth_tracker_db`, accessed via `mysqlclient` |
| **AI / Machine Learning** | scikit-learn & pandas | `CountVectorizer`, `MultinomialNB`, `LinearRegression`, `IsolationForest`, `joblib`, `numpy` |
| **Frontend UI** | HTML5, Vanilla CSS, JS | Bootstrap 5.3 CDN, Bootstrap Icons, Chart.js CDN, Google Fonts (Inter) |
| **Environment** | Windows 11, VS Code | Python virtual environment: `venv` |

---

## 6. Directory Structure Overview
```
wealth_tracker/
├── venv/                       # Python 3.13 virtual environment
└── wealthtracker/              # Project Root (contains manage.py)
    ├── manage.py               # Django management script
    ├── wealthtracker/          # Project configuration package (settings.py, urls.py, wsgi.py)
    ├── tracker/                # Main application package
    │   ├── models/ or models.py# Database schemas (User, Category, Transaction, Budget, Goals, Assets)
    │   ├── views/              # Modular views (auth, dashboard, transactions, budgets, goals, ai, reports)
    │   ├── services/           # Decoupled business logic (stats, budgeting, forecasting, reports)
    │   ├── ml/                 # ML pipelines, vectorizers, regressors, training data, seed CSV
    │   ├── templates/tracker/  # HTML templates inheriting from base.html
    │   ├── static/             # App-specific static assets
    │   └── forms.py            # Form definitions and input validators
    ├── static/                 # Collected project static assets (css, js, images)
    ├── ml_models/              # Persisted joblib models (.joblib files)
    └── docs/                   # Complete architectural, setup, and viva documentation
```

---

## 7. What is In Scope vs. Out of Scope
### In Scope:
- Multi-user authentication with isolated tenant data scoping.
- Income/expense transaction CRUD, category management, recurring reminders.
- Category budgets, overrun warnings, and previous month budget duplication.
- Savings goals with milestone progress and incremental deposits.
- Net worth management (Assets minus Liabilities).
- Chart.js interactive visualizations.
- Machine Learning models (Categorization, Forecasting, Anomaly Detection, Advisory Engine).
- CSV statement import and export.
- Complete viva documentation, test suite, and seed demo data command.

### Out of Scope:
- Live banking Open-Banking APIs (Plaid/Yodlee/Razorpay API integrations requiring proprietary financial licenses).
- Real-time stock trading or live crypto ticker integrations.
- Native mobile apps (Android/iOS binaries) — web application is fully responsive for mobile browsers.
