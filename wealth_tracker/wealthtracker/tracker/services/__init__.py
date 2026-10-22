"""
Smart Wealth Tracker - Business Services Package
Encapsulates domain logic, financial computations, data aggregations, and rule checks.
Follows Fat-Service / Thin-View architecture.
"""

from .dashboard_service import (
    get_financial_summary,
    get_category_expense_breakdown,
    get_cash_flow_trend,
    get_dashboard_context,
)
from .budget_service import (
    get_user_budget_overview,
    check_budget_status,
)
from .goal_service import (
    get_user_goals_overview,
    contribute_to_goal,
)
from .wealth_service import (
    get_net_worth_summary,
)

__all__ = [
    'get_financial_summary',
    'get_category_expense_breakdown',
    'get_cash_flow_trend',
    'get_dashboard_context',
    'get_user_budget_overview',
    'check_budget_status',
    'get_user_goals_overview',
    'contribute_to_goal',
    'get_net_worth_summary',
]
