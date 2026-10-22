from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    icon = models.CharField(max_length=50, default='bi-tag', blank=True, help_text="Bootstrap icon class")
    color = models.CharField(max_length=20, default='#4f46e5', blank=True, help_text="Hex color code")

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TRANSACTION_TYPE = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    PAYMENT_METHODS = (
        ('UPI', 'UPI / GPay / PhonePe'),
        ('Debit Card', 'Debit Card'),
        ('Credit Card', 'Credit Card'),
        ('Net Banking', 'Net Banking'),
        ('Cash', 'Cash'),
        ('Other', 'Other'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField()
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, default='UPI', blank=True)
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'type']),
        ]

    def __str__(self):
        return f"{self.type} - ₹{self.amount} - {self.description or self.category}"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    limit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField()
    year = models.IntegerField()

    class Meta:
        unique_together = ('user', 'category', 'month', 'year')
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.category} - ₹{self.limit_amount} ({self.month}/{self.year})"


class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    goal_name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    saved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField()

    class Meta:
        ordering = ['deadline']

    def __str__(self):
        return f"{self.goal_name} (₹{self.saved_amount}/₹{self.target_amount})"


class Asset(models.Model):
    """Represents positive wealth holdings (bank balances, investments, gold, cash)."""
    ASSET_TYPES = (
        ('bank', 'Bank Account'),
        ('investment', 'Stocks / Mutual Funds'),
        ('real_estate', 'Property / Real Estate'),
        ('gold', 'Gold / Precious Metals'),
        ('cash', 'Cash in Hand'),
        ('crypto', 'Crypto Assets'),
        ('other', 'Other Assets'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assets')
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES, default='bank')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-amount']

    def __str__(self):
        return f"{self.name} - ₹{self.amount}"


class Liability(models.Model):
    """Represents debt obligations (loans, credit card balances, mortgages)."""
    LIABILITY_TYPES = (
        ('loan', 'Personal / Home Loan'),
        ('credit_card', 'Credit Card Due'),
        ('mortgage', 'Mortgage'),
        ('borrowing', 'Informal Borrowing'),
        ('other', 'Other Liabilities'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liabilities')
    name = models.CharField(max_length=100)
    liability_type = models.CharField(max_length=20, choices=LIABILITY_TYPES, default='credit_card')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-amount']

    def __str__(self):
        return f"{self.name} - ₹{self.amount}"