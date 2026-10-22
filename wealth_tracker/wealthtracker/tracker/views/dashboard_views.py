from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from tracker.services.dashboard_service import get_dashboard_context


@login_required
def dashboard_view(request):
    """
    Executive financial dashboard.
    Renders KPI stat cards, dynamic Chart.js donut and bar charts,
    active savings goals progress, recent transaction audit trail,
    and ML spending velocity predictions.
    Delegates all aggregations to dashboard_service.
    """
    context = get_dashboard_context(request.user)
    return render(request, 'tracker/dashboard.html', context)
