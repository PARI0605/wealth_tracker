from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from tracker.forms import BudgetForm
from tracker.services.budget_service import get_user_budget_overview


@login_required
def budget_list_view(request):
    """
    Displays monthly budget limits with dynamic progress bars,
    80% caution thresholds, and overrun warnings.
    Delegates calculations to budget_service.
    """
    budget_data = get_user_budget_overview(request.user)
    return render(request, 'tracker/budget_list.html', {'budget_data': budget_data})


@login_required
def add_budget_view(request):
    """
    Establishes or updates monthly category spending thresholds.
    """
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            return redirect('budget_list')
    else:
        form = BudgetForm(user=request.user)

    return render(request, 'tracker/add_budget.html', {'form': form})
