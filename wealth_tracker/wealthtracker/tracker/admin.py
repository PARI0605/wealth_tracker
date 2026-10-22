from django.contrib import admin
from .models import Category, Transaction, Budget, SavingsGoal, Asset, Liability

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'icon', 'color')
    list_filter = ('user',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'amount', 'category', 'date', 'payment_method')
    list_filter = ('type', 'payment_method', 'date', 'user')
    search_fields = ('description',)

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'limit_amount', 'month', 'year')
    list_filter = ('month', 'year', 'user')

@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal_name', 'target_amount', 'saved_amount', 'deadline')
    list_filter = ('deadline', 'user')

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'asset_type', 'amount', 'updated_at')
    list_filter = ('asset_type', 'user')

@admin.register(Liability)
class LiabilityAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'liability_type', 'amount', 'updated_at')
    list_filter = ('liability_type', 'user')