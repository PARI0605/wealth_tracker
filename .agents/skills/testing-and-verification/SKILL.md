---
name: testing-and-verification
description: Standards for writing Django tests, verifying multi-tenant data isolation, and executing automated test suites for the Smart Wealth Tracker.
---

# Testing and Verification Guide

## When to Use This Skill
Activate this skill after modifying any models, views, services, or ML pipelines to ensure zero regressions, data privacy, and full test suite execution.

---

## 1. Test Execution Commands
Always execute from the project directory (`wealthtracker/`):
```bash
python manage.py test tracker
python manage.py check
```

---

## 2. Test Writing Rules

### Rule 1: Always Test Multi-Tenant Data Isolation
Every view and service test must instantiate at least two distinct users (`user_a` and `user_b`):
```python
def test_user_cannot_access_other_user_transactions(self):
    self.client.login(username='user_b', password='password123')
    response = self.client.get(reverse('transaction_list'))
    self.assertNotContains(response, self.user_a_transaction.description)
```

### Rule 2: Test Financial Calculations with Decimal
```python
from decimal import Decimal
self.assertEqual(balance, Decimal('15000.00'))
```

### Rule 3: Test ML Fallbacks on Empty Cold Starts
Verify that when a brand new user with 0 transactions accesses AI insights, the forecaster and categorizer return graceful fallback defaults without raising exceptions.
