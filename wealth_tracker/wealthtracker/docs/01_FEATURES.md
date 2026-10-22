# 01. Features Specification: Smart Wealth Tracker and Budget Planner

This document provides the complete inventory of all functional and non-functional features, their current status, priorities, and acceptance criteria.

---

## Feature Matrix

| ID | Module / Feature Name | Priority | Status | Acceptance Criteria |
| :--- | :--- | :---: | :---: | :--- |
| **A1** | User Registration & Auto Login | P0 | **Done** | User signs up with username, email, password; auto logs in; creates default categories. |
| **A2** | User Login & Logout | P0 | **Done** | Authenticates credentials; redirect logic based on `next` parameter; dual-panel UI. |
| **A3** | User Profile & Change Password | P2 | **Todo** | User can update personal details and change password securely. |
| **B1** | Transaction Entry (Income/Expense) | P0 | **Done** | Validates positive amount, date, category; associates with `request.user`. |
| **B2** | Transaction List & Deletion | P0 | **Done** | Displays user's transactions; allows safe deletion with confirmation. |
| **B3** | Transaction Editing & Filtering | P1 | **Done** | Edit existing transaction; filter by type, category, date range, search query; pagination. |
| **B4** | CSV Statement Import & Export | P1 | **Done** | Export ledger to CSV; import bank statement CSV with column mapping and AI categorization. |
| **B5** | Recurring Transactions & Reminders | P2 | **Todo** | Mark transactions as recurring; display upcoming bill reminders on dashboard. |
| **C1** | Category Management (CRUD) | P0 | **Done** | Custom categories per user; prevent accidental deletion if transactions linked. |
| **C2** | Category Icons & Colors | P1 | **Done** | Selectable icon (Bootstrap Icons) and color hex code per category; preset suggestion chips. |
| **D1** | Monthly Budget Setting | P0 | **Done** | Assign monthly limit amount per category for a given month and year. |
| **D2** | Budget Progress & Overrun Alert | P0 | **Done** | Visual progress bar; warning at 80%; "Exceeded" state if spending > limit. |
| **D3** | One-Click Budget Rollover | P2 | **Todo** | Copy all category budgets from previous month with a single click. |
| **E1** | Savings Goals Creation | P0 | **Done** | Set goal name, target amount, initial savings, and deadline date. |
| **E2** | Savings Goal Deposits & History | P0 | **Done** | Incremental deposit action; updates saved amount and recalculates progress %. |
| **E3** | Goal Monthly Target Calculator | P1 | **Done** | Calculate required monthly saving velocity in goal_service to achieve goal by deadline. |
| **F1** | Assets & Liabilities Tracking | P1 | **Done** | Models and service calculations for assets & liabilities schema. |
| **F2** | Net Worth Calculation & Trajectory | P1 | **Done** | Compute Net Worth (Assets - Liabilities); debt-to-asset ratio; 6-month trajectory chart. |
| **G1** | Executive Dashboard KPI Cards | P0 | **Done** | Cards for Net Balance, Total Income, Total Expenses, and AI Next Month Forecast. |
| **G2** | Category Expense Donut Chart | P0 | **Done** | Interactive Chart.js donut chart rendering category spending breakdown. |
| **G3** | 6-Month Cash Flow Bar Chart | P0 | **Done** | Interactive Chart.js bar chart comparing income vs expense for last 6 months. |
| **G4** | Month Selector & MoM Change | P1 | **Todo** | Filter dashboard analytics by selected month; show month-over-month % delta. |
| **H1** | Monthly & Yearly Reports | P2 | **Todo** | Summary breakdown, comparative tables, and printable/PDF export view. |
| **I1** | NLP Auto-Categorization | P0 | **Done** | Naive Bayes + CountVectorizer classifying merchant descriptions (Swiggy, Uber, etc.). |
| **I2** | Expense Prediction (Forecasting) | P0 | **Done** | Linear Regression + pandas time-series forecasting of next month's spending burn rate. |
| **I3** | Anomaly Detection | P1 | **Done** | Flag transactions with unusually high deviations via Isolation Forest and Z-score (> 2.0). |
| **I4** | Plain-Language AI Insights Engine | P1 | **Done** | Dynamic financial insights (savings rate, category spikes, subscription burdens). |
| **I5** | AI Budget Recommendations | P2 | **Done** | Suggest and one-click apply category budgets based on 3-month trailing moving averages. |
| **J1** | Public Landing Page | P0 | **Done** | High-converting landing page with live interactive AI classifier demo and CTAs. |
| **J2** | Dark / Light Theme Toggle | P1 | **Done** | Theme switcher persisted in localStorage using CSS variables and Chart.js theme reactivity. |
| **J3** | Seed Demo Data Command | P1 | **Done** | `manage.py seed_demo_data` populating 6 months of realistic Indian transactions, budgets, goals, assets. |
| **J4** | Train ML Models Command | P1 | **Done** | `manage.py train_ml_models` serializing models to `ml_models/` via `joblib`. |

---

## Detailed Acceptance Criteria for Core Modules

### 1. Data Isolation & Security (Critical Rule)
- Every transaction, category, budget, goal, asset, and liability record **must** be foreign-keyed to `auth.User`.
- Every QuerySet executed in views or services **must** be filtered by `user=request.user`.
- No URL pattern or parameter tampering should ever expose another user's financial data.

### 2. Applied Machine Learning (Academic Requirement)
- Models must run with explainable algorithms suitable for viva defense:
  - **Categorization:** Naive Bayes (MultinomialNB) with TF-IDF / Bag of Words (`CountVectorizer`).
  - **Forecasting:** Ordinary Least Squares (OLS) Linear Regression with elapsed month index.
  - **Anomaly Detection:** Outlier detection via Z-Score (> 2.5 std deviations) or Isolation Forest.
- Graceful fallbacks must exist when user history has fewer than 2 monthly data points.

### 3. Financial Exactness
- All currency amounts must be stored and calculated using Python's `Decimal` type to prevent binary floating-point rounding errors.
