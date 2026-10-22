# 04. URLs and Views Routing Guide: Smart Wealth Tracker and Budget Planner

This document catalogs every URL route in the application, its responsible view handler, template, authentication rules, and functional purpose.

---

## Complete Routing Table

| URL Pattern | View Handler | Template | Auth Required? | HTTP Methods | Purpose / Description |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `path('', ...)` | `landing_view` | `tracker/landing.html` | No | `GET` | Public marketing landing page with live interactive AI classifier demo. Auto-redirects to `/dashboard/` if authenticated. |
| `path('home/', ...)` | `landing_view` | `tracker/landing.html` | No | `GET` | Alias for root landing page. |
| `path('signup/', ...)` | `signup_view` | `tracker/signup.html` | No | `GET`, `POST` | Dual-panel user registration form. Auto-logs in on successful creation and provisions default categories. |
| `path('login/', ...)` | `login_view` | `tracker/login.html` | No | `GET`, `POST` | Dual-panel user authentication form. Redirects to `next` URL or `/dashboard/`. |
| `path('logout/', ...)` | `logout_view` | *None (Redirect)* | Yes | `GET`, `POST` | Terminates active user session and redirects to public landing page (`/`). |
| `path('dashboard/', ...)` | `dashboard_view` | `tracker/dashboard.html` | Yes | `GET` | Executive dashboard with KPI summary cards, Chart.js pie and bar charts, active savings goals, and recent ledger. |
| `path('transactions/', ...)` | `transaction_list_view` | `tracker/transaction_list.html` | Yes | `GET` | Full transaction ledger table with search, category filtering, and delete actions. |
| `path('transactions/add/', ...)` | `add_transaction_view` | `tracker/add_transaction.html` | Yes | `GET`, `POST` | Form to record income/expense with live AI categorization helper. Auto-infers category if left blank. |
| `path('transactions/edit/<int:pk>/', ...)` | `edit_transaction_view` | `tracker/edit_transaction.html` | Yes | `GET`, `POST` | Edit existing transaction amount, category, date, or note. |
| `path('transactions/delete/<int:pk>/', ...)`| `delete_transaction_view`| *None (Redirect)* | Yes | `POST` | Securely removes transaction record scoped to `request.user`. |
| `path('transactions/export/csv/', ...)` | `export_transactions_csv` | *None (CSV Stream)* | Yes | `GET` | Streams user's transaction ledger as an attachment CSV file. |
| `path('transactions/import/csv/', ...)` | `import_transactions_csv` | `tracker/import_csv.html` | Yes | `GET`, `POST` | Upload bank CSV with column mapping preview. |
| `path('category/add/', ...)` | `add_category_view` | `tracker/add_category.html` | Yes | `GET`, `POST` | Create a new custom category with icon and color picker. |
| `path('budget/', ...)` | `budget_list_view` | `tracker/budget_list.html` | Yes | `GET` | View category budgets, consumption percentages, and "On Track" / "Exceeded" status badges. |
| `path('budget/add/', ...)` | `add_budget_view` | `tracker/add_budget.html` | Yes | `GET`, `POST` | Assign a new monthly spending limit to a chosen category. |
| `path('budget/rollover/', ...)` | `budget_rollover_view` | *None (Redirect)* | Yes | `POST` | Duplicates active category budgets from previous calendar month to current month. |
| `path('goals/', ...)` | `savings_goal_list_view`| `tracker/savings_goal_list.html` | Yes | `GET` | Savings goals inventory with completion percentages, deadline countdowns, and deposit links. |
| `path('goals/add/', ...)` | `add_savings_goal_view` | `tracker/add_savings_goal.html` | Yes | `GET`, `POST` | Form to create a savings goal with target milestone and deadline date picker. |
| `path('goals/contribute/<int:pk>/', ...)` | `add_savings_contribution_view` | `tracker/add_savings_contribution.html` | Yes | `GET`, `POST` | Deposit funds incrementally into a goal; updates accumulated balance. |
| `path('goals/delete/<int:pk>/', ...)` | `delete_savings_goal_view` | *None (Redirect)* | Yes | `POST` | Delete a savings goal. |
| `path('net-worth/', ...)` | `net_worth_view` | `tracker/net_worth.html` | Yes | `GET` | Net worth calculator: lists assets, liabilities, and net worth balance trajectory. |
| `path('reports/', ...)` | `reports_view` | `tracker/reports.html` | Yes | `GET` | Monthly and annual comparative financial breakdown reports with export options. |
| `path('ai/', ...)` | `ai_insights_view` | `tracker/ai_insights.html` | Yes | `GET` | Dedicated AI Hub with Linear Regression spending forecast, burn velocity, anomaly flags, and interactive NLP testing sandbox. |
| `path('api/predict-category/', ...)` | `predict_category_api` | *JSON Response* | No / Optional | `GET` | Real-time REST API endpoint returning predicted category name and confidence score for any description string. |

---

## Authentication & Authorization Guarantees
- All private views enforce `@login_required(login_url='login')`.
- All object-specific views (`pk` lookups) use `get_object_or_404(Model, pk=pk, user=request.user)` to strictly guarantee that no user can view, edit, or delete another user's financial entities.
