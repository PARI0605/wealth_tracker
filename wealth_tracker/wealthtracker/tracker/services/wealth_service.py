import datetime
from decimal import Decimal
from typing import Dict, Any, List
from django.db.models import Sum
from django.contrib.auth.models import User

from tracker.models import Asset, Liability, Transaction


ASSET_TYPE_COLORS = {
    'bank': '#3b82f6',        # Blue
    'investment': '#10b981',  # Emerald
    'real_estate': '#8b5cf6', # Violet
    'gold': '#f59e0b',        # Amber/Gold
    'cash': '#06b6d4',        # Cyan
    'crypto': '#ec4899',      # Pink
    'other': '#6b7280',       # Gray
}

LIABILITY_TYPE_COLORS = {
    'loan': '#ef4444',        # Red
    'credit_card': '#f97316', # Orange
    'mortgage': '#dc2626',    # Dark Red
    'borrowing': '#eab308',   # Yellow
    'other': '#9ca3af',       # Gray
}


def get_net_worth_summary(user: User) -> Dict[str, Any]:
    """
    Computes comprehensive Net Worth metrics:
      - Total Assets
      - Total Liabilities
      - Net Worth = Total Assets - Total Liabilities
      - Debt-to-Asset ratio
      - Solvency health diagnosis
      - Asset Allocation breakdown (labels, data, colors)
      - Liability Composition breakdown (labels, data, colors)
      - 6-Month historical Net Worth trajectory (labels, data)
    Uses strict Decimal precision and database-level aggregations.
    """
    asset_agg = Asset.objects.filter(user=user).aggregate(total=Sum('amount'))
    liability_agg = Liability.objects.filter(user=user).aggregate(total=Sum('amount'))

    total_assets = asset_agg['total'] or Decimal('0.00')
    total_liabilities = liability_agg['total'] or Decimal('0.00')
    net_worth = total_assets - total_liabilities

    # Debt-to-Asset Ratio
    if total_assets > Decimal('0.00'):
        debt_to_asset_ratio = round((total_liabilities / total_assets) * Decimal('100.0'), 1)
    elif total_liabilities > Decimal('0.00'):
        debt_to_asset_ratio = Decimal('100.0')
    else:
        debt_to_asset_ratio = Decimal('0.0')

    # Solvency Health Indicator
    if total_assets == Decimal('0.00') and total_liabilities == Decimal('0.00'):
        solvency = {
            'label': 'No Holdings Logged',
            'badge': 'secondary',
            'icon': 'bi-info-circle',
            'desc': 'Log your bank accounts, investments, and loans to generate Net Worth analytics.'
        }
    elif net_worth < Decimal('0.00'):
        solvency = {
            'label': 'Negative Net Worth',
            'badge': 'danger',
            'icon': 'bi-exclamation-triangle-fill',
            'desc': 'Total debts exceed current assets. Prioritize aggressive debt clearance.'
        }
    elif debt_to_asset_ratio >= Decimal('50.0'):
        solvency = {
            'label': 'High Leverage',
            'badge': 'warning',
            'icon': 'bi-exclamation-circle-fill',
            'desc': 'Debt represents over 50% of your assets. Recommended to pay down high-interest balances.'
        }
    elif debt_to_asset_ratio >= Decimal('20.0'):
        solvency = {
            'label': 'Healthy Leverage',
            'badge': 'info',
            'icon': 'bi-shield-check',
            'desc': 'Manageable debt structure with solid asset backing.'
        }
    else:
        solvency = {
            'label': 'Strong Financial Health',
            'badge': 'success',
            'icon': 'bi-check-circle-fill',
            'desc': 'Minimal debt and strong asset equity. Excellent financial position.'
        }

    # Asset Allocation Breakdown
    asset_type_dict = dict(Asset.ASSET_TYPES)
    asset_groups = (
        Asset.objects.filter(user=user)
        .values('asset_type')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    asset_labels = []
    asset_data = []
    asset_colors = []
    for g in asset_groups:
        type_key = g['asset_type']
        asset_labels.append(str(asset_type_dict.get(type_key, type_key.title())))
        asset_data.append(float(g['total']))
        asset_colors.append(ASSET_TYPE_COLORS.get(type_key, '#6b7280'))

    # Liability Composition Breakdown
    liability_type_dict = dict(Liability.LIABILITY_TYPES)
    liability_groups = (
        Liability.objects.filter(user=user)
        .values('liability_type')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    liability_labels = []
    liability_data = []
    liability_colors = []
    for g in liability_groups:
        type_key = g['liability_type']
        liability_labels.append(str(liability_type_dict.get(type_key, type_key.title())))
        liability_data.append(float(g['total']))
        liability_colors.append(LIABILITY_TYPE_COLORS.get(type_key, '#ef4444'))

    # 6-Month Net Worth Trajectory
    # Reconstruct monthly net cash flow: net_flow = income - expense
    today = datetime.date.today()
    month_dates = []
    for i in range(5, -1, -1):
        # Calculate month i months ago
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        month_dates.append((year, month))

    monthly_net_flows = []
    trajectory_labels = []
    for (yr, mo) in month_dates:
        inc = Transaction.objects.filter(
            user=user, type='income', date__year=yr, date__month=mo
        ).aggregate(s=Sum('amount'))['s'] or Decimal('0.00')
        exp = Transaction.objects.filter(
            user=user, type='expense', date__year=yr, date__month=mo
        ).aggregate(s=Sum('amount'))['s'] or Decimal('0.00')
        monthly_net_flows.append(inc - exp)
        dt = datetime.date(yr, mo, 1)
        trajectory_labels.append(dt.strftime('%b %Y'))

    # Calculate cumulative back-projection so that current month = net_worth
    # NW[k] = NW[k+1] - flow[k+1]
    trajectory_nw = [Decimal('0.00')] * len(monthly_net_flows)
    trajectory_nw[-1] = net_worth
    for idx in range(len(monthly_net_flows) - 2, -1, -1):
        trajectory_nw[idx] = trajectory_nw[idx + 1] - monthly_net_flows[idx + 1]

    trajectory_data = [float(val) for val in trajectory_nw]

    assets_list = Asset.objects.filter(user=user).order_by('-amount')
    liabilities_list = Liability.objects.filter(user=user).order_by('-amount')

    return {
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'net_worth': net_worth,
        'debt_to_asset_ratio': debt_to_asset_ratio,
        'solvency': solvency,
        'assets': assets_list,
        'liabilities': liabilities_list,
        'asset_labels': asset_labels,
        'asset_data': asset_data,
        'asset_colors': asset_colors,
        'liability_labels': liability_labels,
        'liability_data': liability_data,
        'liability_colors': liability_colors,
        'trajectory_labels': trajectory_labels,
        'trajectory_data': trajectory_data,
    }
