import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional

from django.db.models import Sum
from django.contrib.auth.models import User

from tracker.models import Budget, Transaction, Category


def get_user_budget_overview(
    user: User,
    month: Optional[int] = None,
    year: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Computes category-wise budget consumption, spending vs limit, percentage utilized,
    and alert thresholds for a specific month and year.
    Defaults to the current calendar month if month and year are not specified.
    """
    today = datetime.date.today()
    target_month = month or today.month
    target_year = year or today.year

    budgets = Budget.objects.filter(
        user=user,
        month=target_month,
        year=target_year
    ).select_related('category')

    budget_data: List[Dict[str, Any]] = []

    for b in budgets:
        spent = Transaction.objects.filter(
            user=user,
            category=b.category,
            type='expense',
            date__year=target_year,
            date__month=target_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        limit = b.limit_amount or Decimal('1.00')
        percent = round((spent / limit) * 100) if limit > 0 else 0
        exceeded = spent > limit
        is_caution = (percent >= 80 and not exceeded)
        remaining = max(Decimal('0.00'), limit - spent)
        overrun = max(Decimal('0.00'), spent - limit)

        status = 'exceeded' if exceeded else ('caution' if is_caution else 'on_track')

        budget_data.append({
            'budget': b,
            'spent': spent,
            'limit': limit,
            'percent': percent,
            'remaining': remaining,
            'overrun': overrun,
            'exceeded': exceeded,
            'is_caution': is_caution,
            'status': status,
        })

    return budget_data


def check_budget_status(
    user: User,
    category: Optional[Category],
    additional_amount: Decimal,
    month: Optional[int] = None,
    year: Optional[int] = None
) -> Dict[str, Any]:
    """
    Evaluates whether an impending transaction amount would push the category budget
    into a caution state (>80%) or exceeded state (>100%).
    """
    if not category:
        return {'has_budget': False}

    today = datetime.date.today()
    target_month = month or today.month
    target_year = year or today.year

    budget = Budget.objects.filter(
        user=user,
        category=category,
        month=target_month,
        year=target_year
    ).first()

    if not budget:
        return {'has_budget': False}

    current_spent = Transaction.objects.filter(
        user=user,
        category=category,
        type='expense',
        date__year=target_year,
        date__month=target_month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    projected_spent = current_spent + additional_amount
    limit = budget.limit_amount

    projected_percent = round((projected_spent / limit) * 100) if limit > 0 else 0
    will_exceed = projected_spent > limit
    will_warn = projected_percent >= 80 and not will_exceed

    return {
        'has_budget': True,
        'limit': limit,
        'current_spent': current_spent,
        'projected_spent': projected_spent,
        'projected_percent': projected_percent,
        'will_exceed': will_exceed,
        'will_warn': will_warn,
    }
