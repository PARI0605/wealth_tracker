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
from tracker.models import Asset, Liability
from tracker.services.wealth_service import get_net_worth_summary

print("=== STARTING PHASE 4 AUTOMATED COMPREHENSIVE VERIFICATION ===")

client = Client()

# 1. Authenticate user shadow
login_success = client.login(username='shadow', password='shadow123')
assert login_success, "Login failed for shadow"
user = User.objects.get(username='shadow')
print("[PASS] User 'shadow' authenticated")

# 2. Test Net Worth Dashboard GET
resp = client.get('/net-worth/')
assert resp.status_code == 200, f"Net worth dashboard failed: {resp.status_code}"
assert b'Net Worth &amp; Balance Sheet' in resp.content or b'Net Worth & Balance Sheet' in resp.content, "Net Worth header missing"
assert b'netWorthTrajectoryChart' in resp.content, "Trajectory chart canvas missing"
assert b'assetAllocationChart' in resp.content, "Asset allocation canvas missing"
assert b'quickAddAssetModal' in resp.content, "Quick Add Asset modal missing"
assert b'quickAddLiabilityModal' in resp.content, "Quick Add Liability modal missing"
print("[PASS] Net Worth Dashboard renders KPI cards, Chart.js canvases, tables, and quick-add modals (HTTP 200)")

# 3. Test Add Asset GET & POST
resp = client.get('/assets/add/')
assert resp.status_code == 200, f"Add asset GET failed: {resp.status_code}"
assert b'Add Asset to Portfolio' in resp.content
print("[PASS] Add Asset GET renders clean fintech form (HTTP 200)")

resp = client.post('/assets/add/', {
    'name': 'Zerodha Equity Portfolio',
    'asset_type': 'investment',
    'amount': '125000.00'
}, follow=True)
assert resp.status_code == 200
new_asset = Asset.objects.filter(user=user, name='Zerodha Equity Portfolio').first()
assert new_asset is not None, "Asset was not created in database"
assert new_asset.amount == Decimal('125000.00'), f"Unexpected amount: {new_asset.amount}"
print(f"[PASS] Add Asset POST successfully created asset #{new_asset.pk} of INR {new_asset.amount}")

# 4. Test Edit Asset GET & POST
resp = client.get(f'/assets/edit/{new_asset.pk}/')
assert resp.status_code == 200
assert b'Edit Asset Holding' in resp.content

resp = client.post(f'/assets/edit/{new_asset.pk}/', {
    'name': 'Zerodha Nifty ETF',
    'asset_type': 'investment',
    'amount': '150000.00'
}, follow=True)
assert resp.status_code == 200
new_asset.refresh_from_db()
assert new_asset.name == 'Zerodha Nifty ETF'
assert new_asset.amount == Decimal('150000.00')
print(f"[PASS] Edit Asset POST updated asset to '{new_asset.name}' (INR {new_asset.amount})")

# 5. Test Add Liability GET & POST
resp = client.get('/liabilities/add/')
assert resp.status_code == 200
assert b'Record Liability / Debt' in resp.content
print("[PASS] Add Liability GET renders clean debt form (HTTP 200)")

resp = client.post('/liabilities/add/', {
    'name': 'HDFC Millennia Credit Card',
    'liability_type': 'credit_card',
    'amount': '25000.00'
}, follow=True)
assert resp.status_code == 200
new_debt = Liability.objects.filter(user=user, name='HDFC Millennia Credit Card').first()
assert new_debt is not None
assert new_debt.amount == Decimal('25000.00')
print(f"[PASS] Add Liability POST successfully recorded debt #{new_debt.pk} of INR {new_debt.amount}")

# 6. Test Edit Liability GET & POST
resp = client.get(f'/liabilities/edit/{new_debt.pk}/')
assert resp.status_code == 200
assert b'Edit Debt Obligation' in resp.content

resp = client.post(f'/liabilities/edit/{new_debt.pk}/', {
    'name': 'HDFC Card Cleared Balance',
    'liability_type': 'credit_card',
    'amount': '12000.00'
}, follow=True)
assert resp.status_code == 200
new_debt.refresh_from_db()
assert new_debt.name == 'HDFC Card Cleared Balance'
assert new_debt.amount == Decimal('12000.00')
print(f"[PASS] Edit Liability POST updated debt to '{new_debt.name}' (INR {new_debt.amount})")

# 7. Test Wealth Service Metrics
summary = get_net_worth_summary(user)
assert summary['total_assets'] >= Decimal('150000.00')
assert summary['total_liabilities'] >= Decimal('12000.00')
assert summary['net_worth'] == summary['total_assets'] - summary['total_liabilities']
assert len(summary['trajectory_labels']) == 6
assert len(summary['trajectory_data']) == 6
print(f"[PASS] Wealth Service calculated Net Worth: INR {summary['net_worth']}, Debt Ratio: {summary['debt_to_asset_ratio']}%")

# 8. Test Sidebar Navigation & Dashboard Link
resp = client.get('/dashboard/')
assert resp.status_code == 200
assert b'/net-worth/' in resp.content, "Net Worth link missing in dashboard/sidebar"
print("[PASS] Dashboard and Sidebar render clickable Net Worth links")

# 9. Clean up test records
new_asset.delete()
new_debt.delete()
print("[PASS] Test asset and liability records safely cleaned up")

print("\n=== ALL 9 PHASE 4 INTEGRATION CHECKS PASSED WITH 100% SUCCESS! ===")
