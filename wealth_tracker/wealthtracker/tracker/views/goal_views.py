from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from tracker.models import SavingsGoal
from tracker.forms import SavingsGoalForm
from tracker.services.goal_service import get_user_goals_overview, contribute_to_goal


@login_required
def savings_goal_list_view(request):
    """
    Displays milestone goals, countdowns, and progress rings.
    Delegates calculations to goal_service.
    """
    goals_data = get_user_goals_overview(request.user)
    return render(request, 'tracker/savings_goal_list.html', {'goals_data': goals_data})


@login_required
def add_savings_goal_view(request):
    """
    Creates a new target savings milestone.
    """
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('savings_goal_list')
    else:
        form = SavingsGoalForm()

    return render(request, 'tracker/add_savings_goal.html', {'form': form})


@login_required
def add_savings_contribution_view(request, pk: int):
    """
    Processes deposit contribution towards a savings goal.
    """
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)

    if request.method == 'POST':
        raw_amount = request.POST.get('amount')
        try:
            amt = Decimal(raw_amount)
            if amt > Decimal('0.00'):
                _, _, _, is_completed = contribute_to_goal(request.user, goal.pk, amt)
                if is_completed:
                    messages.success(request, f"🎉 Congratulations! You have fully achieved your goal: '{goal.goal_name}'!")
                else:
                    messages.success(request, f"Successfully deposited ₹{amt} into '{goal.goal_name}'.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid deposit amount entered.")

        return redirect('savings_goal_list')

    return render(request, 'tracker/add_savings_contribution.html', {'goal': goal})


@login_required
def delete_savings_goal_view(request, pk: int):
    """
    Deletes a savings goal record with strict tenant isolation.
    """
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    goal.delete()
    return redirect('savings_goal_list')
