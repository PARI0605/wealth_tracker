import json
import datetime
import calendar
from decimal import Decimal
from typing import Dict, Any, List, Tuple

from django.db.models import Sum
from django.contrib.auth.models import User

from tracker.models import Transaction, SavingsGoal
from tracker.ai import predict_expenses, generate_financial_insights


def get_financial_summary(user: User) -> Dict[str, Decimal]:
    """
    Computes total recorded income, total expenses, and current net balance for a user.
    Uses database-level SUM aggregations for maximum performance and exact Decimal math.
    """
    income_agg = Transaction.objects.filter(user=user, type='income').aggregate(total=Sum('amount'))
    expense_agg = Transaction.objects.filter(user=user, type='expense').aggregate(total=Sum('amount'))

    total_income = income_agg['total'] or Decimal('0.00')
    total_expense = expense_agg['total'] or Decimal('0.00')
    balance = total_income - total_expense

    return {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
    }


def get_category_expense_breakdown(user: User) -> Tuple[List[str], List[float]]:
    """
    Computes spending grouped by category for donut/pie chart visualization.
    Returns:
        labels: List of category names
        data: List of aggregated amounts (floats for Chart.js compatibility)
    """
    cat_expenses = (
        Transaction.objects.filter(user=user, type='expense')
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    labels = [c['category__name'] or 'Uncategorized' for c in cat_expenses]
    data = [float(c['total']) for c in cat_expenses]

    return labels, data


def get_cash_flow_trend(user: User, months: int = 6) -> Tuple[List[str], List[float], List[float]]:
    """
    Generates trailing monthly cash flow metrics (Income vs Expense) for comparative bar chart.
    Parameters:
        user: Active User instance
        months: Number of trailing months to include (default 6)
    Returns:
        labels: List of month short names (e.g. ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'])
        income_series: List of total income per month
        expense_series: List of total expenses per month
    """
    today = datetime.date.today()
    labels: List[str] = []
    income_series: List[float] = []
    expense_series: List[float] = []

    for i in range(months - 1, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1

        month_name = calendar.month_abbr[m]
        labels.append(month_name)

        inc = Transaction.objects.filter(
            user=user,
            type='income',
            date__year=y,
            date__month=m
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        exp = Transaction.objects.filter(
            user=user,
            type='expense',
            date__year=y,
            date__month=m
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        income_series.append(float(inc))
        expense_series.append(float(exp))

    return labels, income_series, expense_series


def get_dashboard_context(user: User) -> Dict[str, Any]:
    """
    Aggregates complete context payload for executive dashboard view.
    Includes KPI summaries, Chart.js serializations, recent transactions,
    savings goals progress, and AI forecasts.
    """
    summary = get_financial_summary(user)
    pie_labels, pie_data = get_category_expense_breakdown(user)
    bar_labels, bar_income, bar_expense = get_cash_flow_trend(user, months=6)

    # Recent transaction audit trail (latest 10)
    recent_transactions = Transaction.objects.filter(user=user).select_related('category').order_by('-date')[:10]

    # Active savings goals enriched with completion percentages
    raw_goals = list(SavingsGoal.objects.filter(user=user).order_by('deadline'))
    for g in raw_goals:
        pct = round((g.saved_amount / g.target_amount) * 100) if g.target_amount > 0 else 0
        g.percent = min(100, pct)
        g.is_completed = g.saved_amount >= g.target_amount

    # AI ML Forecasting
    ai_data = predict_expenses(user)

    return {
        'total_income': summary['total_income'],
        'total_expense': summary['total_expense'],
        'balance': summary['balance'],
        'transactions': recent_transactions,
        # Chart.js Serialized Data
        'pie_labels': json.dumps(pie_labels),
        'pie_data': json.dumps(pie_data),
        'bar_labels': json.dumps(bar_labels),
        'bar_income': json.dumps(bar_income),
        'bar_expense': json.dumps(bar_expense),
        # Intelligence & Milestones
        'ai_data': ai_data,
        'financial_insights': generate_financial_insights(user),
        'savings_goals': raw_goals,
    }
