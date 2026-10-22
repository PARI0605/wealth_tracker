from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('home/', views.landing_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('transactions/', views.transaction_list_view, name='transaction_list'),
    path('transactions/add/', views.add_transaction_view, name='add_transaction'),
    path('transactions/edit/<int:pk>/', views.edit_transaction_view, name='edit_transaction'),
    path('transactions/delete/<int:pk>/', views.delete_transaction_view, name='delete_transaction'),
    path('transactions/export/csv/', views.export_transactions_csv, name='export_transactions_csv'),
    path('transactions/import/csv/', views.import_transactions_csv, name='import_transactions_csv'),
    path('category/add/', views.add_category_view, name='add_category'),
    path('category/delete/<int:pk>/', views.delete_category_view, name='delete_category'),
    path('budget/add/', views.add_budget_view, name='add_budget'),
    path('budget/', views.budget_list_view, name='budget_list'),
    path('budget/apply-recommendation/', views.apply_budget_recommendation_view, name='apply_budget_recommendation'),

    # Module 8: Savings Goal Tracker
    path('goals/', views.savings_goal_list_view, name='savings_goal_list'),
    path('goals/add/', views.add_savings_goal_view, name='add_savings_goal'),
    path('goals/delete/<int:pk>/', views.delete_savings_goal_view, name='delete_savings_goal'),
    path('goals/contribute/<int:pk>/', views.add_savings_contribution_view, name='add_savings_contribution'),

    # Phase 4: Net Worth Module
    path('net-worth/', views.net_worth_view, name='net_worth'),
    path('assets/add/', views.add_asset_view, name='add_asset'),
    path('assets/edit/<int:pk>/', views.edit_asset_view, name='edit_asset'),
    path('assets/delete/<int:pk>/', views.delete_asset_view, name='delete_asset'),
    path('liabilities/add/', views.add_liability_view, name='add_liability'),
    path('liabilities/edit/<int:pk>/', views.edit_liability_view, name='edit_liability'),
    path('liabilities/delete/<int:pk>/', views.delete_liability_view, name='delete_liability'),

    # Module 7: AI/ML
    path('ai/', views.ai_insights_view, name='ai_insights'),
    path('api/predict-category/', views.predict_category_api, name='predict_category_api'),
]