import datetime
from decimal import Decimal
from typing import List, Dict, Any, Tuple

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db import transaction

from tracker.models import SavingsGoal


def get_user_goals_overview(user: User) -> List[Dict[str, Any]]:
    """
    Computes progress milestones, remaining balances, days left, and required monthly
    deposit rate for all savings goals belonging to the user.
    """
    today = datetime.date.today()
    goals = SavingsGoal.objects.filter(user=user).order_by('deadline')
    goals_data: List[Dict[str, Any]] = []

    for g in goals:
        target = g.target_amount or Decimal('1.00')
        saved = g.saved_amount or Decimal('0.00')
        percent = round((saved / target) * 100) if target > 0 else 0
        remaining = max(Decimal('0.00'), target - saved)
        days_left = (g.deadline - today).days
        is_completed = saved >= target
        is_overdue = days_left < 0 and not is_completed

        # Calculate monthly recommended saving velocity
        if not is_completed and days_left > 0:
            months_left = max(Decimal('1.0'), Decimal(str(days_left)) / Decimal('30.417'))
            monthly_rate = (remaining / months_left).quantize(Decimal('0.01'))
        else:
            monthly_rate = Decimal('0.00')

        if is_completed:
            status = 'completed'
        elif is_overdue:
            status = 'overdue'
        else:
            status = 'in_progress'

        goals_data.append({
            'goal': g,
            'percent': min(100, percent),
            'remaining': remaining,
            'days_left': days_left,
            'is_completed': is_completed,
            'is_overdue': is_overdue,
            'status': status,
            'monthly_rate': monthly_rate,
        })

    return goals_data


def contribute_to_goal(user: User, goal_id: int, amount: Decimal) -> Tuple[SavingsGoal, Decimal, int, bool]:
    """
    Safely adds funds towards a user's savings goal within an atomic transaction.
    Parameters:
        user: Owner of the goal
        goal_id: Primary key of SavingsGoal
        amount: Decimal amount to deposit
    Returns:
        (goal, new_saved_total, new_percent, is_completed)
    """
    if amount <= Decimal('0.00'):
        raise ValueError("Contribution amount must be greater than zero.")

    with transaction.atomic():
        goal = get_object_or_404(SavingsGoal, pk=goal_id, user=user)
        goal.saved_amount = (goal.saved_amount or Decimal('0.00')) + amount
        goal.save()

        target = goal.target_amount or Decimal('1.00')
        percent = round((goal.saved_amount / target) * 100) if target > 0 else 0
        is_completed = goal.saved_amount >= target

        return goal, goal.saved_amount, percent, is_completed
