import sys
import os
import django
from decimal import Decimal

# Set up Django environment
sys.path.append(r'c:\Users\Parinika\OneDrive\Desktop\wealth_tracker\wealth_tracker\wealthtracker')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wealthtracker.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from tracker.models import Category, Transaction, Budget
from tracker.ai import (
    predict_category,
    predict_expenses,
    detect_anomalies,
    get_transaction_anomaly_ids,
    generate_budget_recommendations,
    generate_financial_insights,
)

print("=== STARTING PHASE 5 AUTOMATED COMPREHENSIVE VERIFICATION ===")

client = Client()

# 1. Authenticate user shadow
login_success = client.login(username='shadow', password='shadow123')
assert login_success, "Login failed for shadow"
user = User.objects.get(username='shadow')
print("[PASS] User 'shadow' authenticated")

# 2. Test AI Hub GET (HTTP 200 and all Phase 5 sections)
resp = client.get('/ai/')
assert resp.status_code == 200, f"AI Hub failed: {resp.status_code}"
assert b'Spending Anomaly Detection Radar' in resp.content, "Anomaly radar section missing"
assert b'AI Smart Budget Recommendations' in resp.content, "Budget recommendations missing"
assert b'Plain-Language Financial Insights Engine' in resp.content, "Insights engine section missing"
assert b'Live Naive Bayes NLP Categorization Sandbox' in resp.content, "Sandbox missing"
assert b'Time-Series Linear Regression Model Details' in resp.content, "Regression details missing"
print("[PASS] AI Hub renders all 5 intelligence modules (HTTP 200)")

# 3. Test Anomaly Detection Engine
food_cat = Category.objects.filter(user=user, name__icontains='Food').first() or Category.objects.filter(user=user).first()
# Create regular transactions
for i in range(4):
    Transaction.objects.create(
        user=user,
        amount=Decimal('350.00'),
        category=food_cat,
        type='expense',
        description=f'Normal lunch {i+1}',
        date='2026-10-15'
    )

# Create a clear spike anomaly
spike = Transaction.objects.create(
    user=user,
    amount=Decimal('22000.00'),
    category=food_cat,
    type='expense',
    description='Grand Luxury 5-Star Hotel Banquet',
    date='2026-10-16'
)

anomalies = detect_anomalies(user, threshold_z=2.0)
assert len(anomalies) >= 1, "Expected at least 1 anomaly flagged"
spike_flag = next((a for a in anomalies if a['transaction'].pk == spike.pk), None)
assert spike_flag is not None, "Spike transaction was not flagged as an anomaly"
assert spike_flag['z_score'] >= 2.0
assert 'higher than your average' in spike_flag['reason']
print(f"[PASS] Anomaly Engine flagged transaction #{spike.pk} with Z = +{spike_flag['z_score']} (Severity: {spike_flag['severity']})")

# 4. Test Transaction Ledger Anomaly Badge
anomaly_ids = get_transaction_anomaly_ids(user)
assert spike.pk in anomaly_ids
resp = client.get('/transactions/')
assert resp.status_code == 200
assert b'Unusual Spend' in resp.content, "Anomaly badge missing in transaction ledger HTML"
print("[PASS] Transaction Ledger displays 'Unusual Spend' warning badge on flagged anomaly")

# 5. Test AI Budget Recommendations Engine
recs = generate_budget_recommendations(user)
assert len(recs) >= 1, "Expected at least 1 budget recommendation"
food_rec = next((r for r in recs if r['category'].pk == food_cat.pk), None)
assert food_rec is not None
assert food_rec['recommended_limit'] >= Decimal('500.00')
print(f"[PASS] AI Budget Recommendation generated for '{food_cat.name}': Recommended limit INR {food_rec['recommended_limit']}")

# 6. Test One-Click Apply Budget Recommendation
resp = client.post('/budget/apply-recommendation/', {
    'category_id': food_cat.pk,
    'amount': str(food_rec['recommended_limit'])
}, follow=True)
assert resp.status_code == 200
import datetime
today = datetime.date.today()
applied_budget = Budget.objects.filter(user=user, category=food_cat, month=today.month, year=today.year).first()
assert applied_budget is not None
assert applied_budget.limit_amount == food_rec['recommended_limit']
print(f"[PASS] One-Click Apply Budget updated Budget #{applied_budget.pk} to INR {applied_budget.limit_amount}")

# 7. Test Plain-Language AI Insights Engine
insights = generate_financial_insights(user)
assert len(insights) >= 1
first_ins = insights[0]
assert 'title' in first_ins and 'body' in first_ins
print(f"[PASS] Financial Insights Engine generated: '{first_ins['title']}'")

# 8. Test Dashboard AI Advisory Banner
resp = client.get('/dashboard/')
assert resp.status_code == 200
assert b'AI Intelligence &amp; Spending Advisory' in resp.content or b'AI Intelligence & Spending Advisory' in resp.content
print("[PASS] Dashboard features dynamic AI Intelligence & Spending Advisory banner")

# 9. Clean up test spike transaction
spike.delete()
print("[PASS] Test spike transaction cleaned up")

print("\n=== ALL 9 PHASE 5 INTEGRATION CHECKS PASSED WITH 100% SUCCESS! ===")
