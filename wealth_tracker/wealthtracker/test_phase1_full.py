import sys
import os
import django
from decimal import Decimal

# Set up Django environment
sys.path.append(r'c:\Users\Parinika\OneDrive\Desktop\wealth_tracker\wealth_tracker\wealthtracker')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wealthtracker.settings')
django.setup()

from django.conf import settings
from django.test import Client
from django.contrib.auth.models import User
from tracker.models import Category, Transaction, Budget, SavingsGoal

print("=== STARTING PHASE 1 AUTOMATED COMPREHENSIVE VERIFICATION ===")

client = Client()

# 1. Test unauthenticated landing page
resp = client.get('/')
assert resp.status_code == 200, f"Landing page failed with {resp.status_code}"
assert b'WealthTracker' in resp.content, "Landing page missing brand logo"
assert b'Smarter Personal Wealth' in resp.content or b'Financial Intelligence' in resp.content, "Hero content missing"
print("[PASS] Unauthenticated visitor receives Public Landing Page (HTTP 200)")

# 2. Test login
login_success = client.login(username='shadow', password='shadow123')
assert login_success, "Login failed for shadow/shadow123"
print("[PASS] Authenticated session established for test user 'shadow'")

# 3. Test root redirect for logged in user
resp = client.get('/', follow=False)
assert resp.status_code == 302 and resp.url == '/dashboard/', f"Expected 302 to /dashboard/, got {resp.status_code} to {resp.url}"
print("[PASS] Authenticated user visiting '/' is auto-redirected to '/dashboard/' (HTTP 302 -> /dashboard/)")

# 4. Test Dashboard
resp = client.get('/dashboard/')
assert resp.status_code == 200, f"Dashboard failed with {resp.status_code}"
assert b'Financial Dashboard' in resp.content, "Dashboard title missing"
assert b'Net Balance' in resp.content, "KPI Net Balance missing"
if getattr(settings, 'SHOW_AI_FEATURES', False):
    assert b'AI Forecast' in resp.content, "AI Forecast card missing"
else:
    assert b'AI Forecast' not in resp.content, "AI Forecast card should be hidden when SHOW_AI_FEATURES is False"
assert b'categoryPieChart' in resp.content, "Chart.js donut canvas missing"
assert b'incomeExpenseBarChart' in resp.content, "Chart.js bar canvas missing"
assert b'appSidebar' in resp.content, "Sidebar element missing"
assert b'quickAddModal' in resp.content, "Quick Add Modal missing"
print("[PASS] Dashboard renders KPI cards, Chart.js canvases, sidebar, and quick-add modal (HTTP 200)")

# 5. Test Transactions List
resp = client.get('/transactions/')
assert resp.status_code == 200, f"Transactions list failed with {resp.status_code}"
assert b'Transaction Ledger' in resp.content, "Ledger title missing"
assert b'ledgerSearchInput' in resp.content, "Client search filter input missing"
print("[PASS] Transaction Ledger renders with live search toolbar (HTTP 200)")

# 6. Test Add Transaction Form
resp = client.get('/transactions/add/')
assert resp.status_code == 200, f"Add transaction failed with {resp.status_code}"
assert b'Record Transaction' in resp.content, "Add transaction title missing"
if getattr(settings, 'SHOW_AI_FEATURES', False):
    assert b'AI Smart Auto-Tag' in resp.content, "AI Helper missing"
    print("[PASS] Add Transaction form renders with Bootstrap 5 input group and AI Auto-Tag (HTTP 200)")
else:
    assert b'AI Smart Auto-Tag' not in resp.content, "AI Helper should be hidden"
    print("[PASS] Add Transaction form renders with Bootstrap 5 input group (HTTP 200)")
assert b'input-group' in resp.content, "Bootstrap input group missing"

# 7. Test AI Prediction API endpoint
resp = client.get('/api/predict-category/?desc=Swiggy%20order')
assert resp.status_code == 200, f"AI predict endpoint failed with {resp.status_code}"
import json
data = json.loads(resp.content)
assert 'predicted_category' in data and data['predicted_category'] is not None, f"Prediction missing: {data}"
print(f"[PASS] AI Prediction API returned: {data['predicted_category']} with {data['confidence']}% confidence (HTTP 200)")

# 8. Test Add Category Page
resp = client.get('/category/add/')
assert resp.status_code == 200, f"Add category failed with {resp.status_code}"
assert b'Financial Categories' in resp.content, "Add category title missing"
assert b'suggestion-chip' in resp.content, "Quick suggestion chips missing"
print("[PASS] Add Category renders with one-click suggestion chips (HTTP 200)")

# 9. Test Budget List & Add Budget
resp = client.get('/budget/')
assert resp.status_code == 200, f"Budget list failed with {resp.status_code}"
assert b'Monthly Budgets' in resp.content, "Budget list title missing"
resp = client.get('/budget/add/')
assert resp.status_code == 200, f"Add budget failed with {resp.status_code}"
assert b'Set Monthly Budget' in resp.content, "Add budget title missing"
print("[PASS] Budget List and Add Budget pages render cleanly (HTTP 200)")

# 10. Test Savings Goals List & Add Goal
resp = client.get('/goals/')
assert resp.status_code == 200, f"Goals list failed with {resp.status_code}"
assert b'Savings Goal Tracker' in resp.content, "Goals title missing"
resp = client.get('/goals/add/')
assert resp.status_code == 200, f"Add goal failed with {resp.status_code}"
assert b'Establish Savings Goal' in resp.content, "Add goal title missing"
print("[PASS] Savings Goals List and Add Goal pages render cleanly (HTTP 200)")

# 11. Test AI Hub
if getattr(settings, 'SHOW_AI_FEATURES', False):
    resp = client.get('/ai/')
    assert resp.status_code == 200, f"AI hub failed with {resp.status_code}"
    assert b'AI &amp; Machine Learning Hub' in resp.content or b'AI & Machine Learning Hub' in resp.content, "AI hub title missing"
    assert b'Linear Regression Model Details' in resp.content, "Regression table missing"
    assert b'Naive Bayes NLP Categorization Sandbox' in resp.content, "NLP sandbox missing"
    print("[PASS] AI Hub renders Linear Regression metrics, forecast cards, and NLP sandbox (HTTP 200)")
else:
    resp = client.get('/ai/')
    assert resp.status_code == 302, f"AI hub should redirect (HTTP 302) when SHOW_AI_FEATURES is False, got: {resp.status_code}"
    print("[PASS] AI Hub cleanly redirects (HTTP 302) when AI features are hidden")

print("\n=== ALL 11 PHASE 1 VERIFICATION TESTS PASSED SUCCESSFULLY! ===")
