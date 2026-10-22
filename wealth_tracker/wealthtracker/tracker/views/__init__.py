"""
Smart Wealth Tracker - Views Package
Modular view controllers re-exported for URL routing.
"""

from .auth_views import (
    landing_view,
    signup_view,
    login_view,
    logout_view,
)
from .dashboard_views import (
    dashboard_view,
)
from .transaction_views import (
    transaction_list_view,
    add_transaction_view,
    edit_transaction_view,
    delete_transaction_view,
    export_transactions_csv,
    import_transactions_csv,
    add_category_view,
    delete_category_view,
)
from .budget_views import (
    budget_list_view,
    add_budget_view,
)
from .goal_views import (
    savings_goal_list_view,
    add_savings_goal_view,
    add_savings_contribution_view,
    delete_savings_goal_view,
)
from .wealth_views import (
    net_worth_view,
    add_asset_view,
    edit_asset_view,
    delete_asset_view,
    add_liability_view,
    edit_liability_view,
    delete_liability_view,
)
from .ai_views import (
    ai_insights_view,
    predict_category_api,
    apply_budget_recommendation_view,
)

__all__ = [
    'landing_view',
    'signup_view',
    'login_view',
    'logout_view',
    'dashboard_view',
    'transaction_list_view',
    'add_transaction_view',
    'edit_transaction_view',
    'delete_transaction_view',
    'export_transactions_csv',
    'import_transactions_csv',
    'add_category_view',
    'delete_category_view',
    'budget_list_view',
    'add_budget_view',
    'savings_goal_list_view',
    'add_savings_goal_view',
    'add_savings_contribution_view',
    'delete_savings_goal_view',
    'net_worth_view',
    'add_asset_view',
    'edit_asset_view',
    'delete_asset_view',
    'add_liability_view',
    'edit_liability_view',
    'delete_liability_view',
    'ai_insights_view',
    'predict_category_api',
    'apply_budget_recommendation_view',
]

