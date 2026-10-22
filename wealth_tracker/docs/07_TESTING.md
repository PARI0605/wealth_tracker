# 07. Testing Strategy & Verification Checklist

This document describes the automated test strategy, test execution commands, and manual verification checklists for the Smart Wealth Tracker.

---

## 1. Test Architecture
Tests are located in `tracker/tests/`:
1. **Model Tests (`test_models.py`):** Validates field constraints, positive amount validators, unique together constraints, and string representations.
2. **Service Tests (`test_services.py`):** Unit tests for business logic (KPI summary totals, budget consumption percentages, goal remaining calculations).
3. **ML Pipeline Tests (`test_ml.py`):** Tests Naive Bayes inference accuracy, CountVectorizer handling of unknown tokens, and Linear Regression forecasting boundary conditions.
4. **View & Security Tests (`test_views.py`):**
   - Authentication gates (`@login_required` redirects).
   - Multi-tenant data isolation: Confirms User A cannot read, modify, or delete records belonging to User B.
   - CSRF protection validation.

---

## 2. Test Execution Commands

Run all tests:
```bash
python manage.py test tracker
```

Run specific test modules:
```bash
python manage.py test tracker.tests.test_models
python manage.py test tracker.tests.test_services
python manage.py test tracker.tests.test_ml
python manage.py test tracker.tests.test_views
```

Run system check:
```bash
python manage.py check
```

---

## 3. Manual Testing & Viva Demonstration Checklist

| Checkpoint | Action | Expected Result | Verified? |
| :--- | :--- | :--- | :---: |
| **1. Public Flow** | Visit `http://127.0.0.1:8000/` unauthenticated | Renders Public Landing Page with Hero preview and features. | [x] |
| **2. Interactive AI** | Test "Starbucks latte" on landing page | Real-time classification responds with `Food` and confidence. | [x] |
| **3. Dual-Panel Auth**| Visit `/login/` | Renders split screen: visual showcase on left, form on right. | [x] |
| **4. Login Redirect** | Enter `shadow` / `shadow123` | Redirects cleanly to `/dashboard/`. | [x] |
| **5. Dashboard Visuals**| Inspect `/dashboard/` | Donut chart renders category split; Bar chart renders 6 months. | [x] |
| **6. Add Transaction**| Add ₹500 description "Uber cab" | AI button auto-fills "Transportation"; balance updates. | [x] |
| **7. Budget Progress** | Check `/budget/` | Progress bar updates; warning badge if > 80% or exceeded. | [x] |
| **8. Savings Goal** | Visit `/goals/`, deposit ₹2,000 | Saved amount increments, progress bar percentage advances. | [x] |
| **9. AI Hub** | Visit `/ai/` | Displays Linear Regression forecast, burn rate, and test form. | [x] |
| **10. Data Isolation** | Log in as different user | No transactions or budgets of User A appear for User B. | [x] |
| **11. Logout Flow** | Click Logout in navbar | Terminates session, redirects cleanly to public landing page. | [x] |
