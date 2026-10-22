from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Transaction, Category, Budget, SavingsGoal, Asset, Liability


class BootstrapFormMixin:
    """Helper mixin to automatically apply Bootstrap 5 form classes to all widgets."""
    def apply_bootstrap_classes(self):
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                existing_class = widget.attrs.get('class', '')
                widget.attrs['class'] = f"form-select {existing_class}".strip()
            elif isinstance(widget, forms.CheckboxInput):
                existing_class = widget.attrs.get('class', '')
                widget.attrs['class'] = f"form-check-input {existing_class}".strip()
            elif isinstance(widget, (forms.TextInput, forms.NumberInput, forms.EmailInput, forms.DateInput, forms.Textarea)):
                existing_class = widget.attrs.get('class', '')
                widget.attrs['class'] = f"form-control {existing_class}".strip()


class SignUpForm(UserCreationForm, BootstrapFormMixin):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_classes()
        self.fields['username'].widget.attrs.update({'placeholder': 'Choose username'})
        self.fields['email'].widget.attrs.update({'placeholder': 'name@example.com'})


ICON_CHOICES = (
    ('bi-tag', '🏷️ Generic Tag'),
    ('bi-cup-hot', '🍔 Food & Dining'),
    ('bi-car-front', '🚗 Transportation & Fuel'),
    ('bi-cart3', '🛒 Groceries'),
    ('bi-house-door', '🏠 Housing & Rent'),
    ('bi-lightning-charge', '💡 Utilities & Bills'),
    ('bi-film', '🎬 Entertainment & OTT'),
    ('bi-heart-pulse', '🏥 Healthcare & Meds'),
    ('bi-bag', '🛍️ Shopping & Apparel'),
    ('bi-cash-coin', '💼 Salary & Income'),
    ('bi-graph-up-arrow', '📈 Investments & Stocks'),
    ('bi-airplane', '✈️ Travel & Holidays'),
    ('bi-book', '📚 Education & Books'),
)


class TransactionForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = Transaction
        fields = ['amount', 'category', 'type', 'description', 'date', 'payment_method', 'is_recurring']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'placeholder': '0.00'}),
            'description': forms.TextInput(attrs={'placeholder': 'e.g. Swiggy, Uber ride, Grocery, Salary...', 'id': 'id_description'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
        self.apply_bootstrap_classes()
        if 'category' in self.fields:
            self.fields['category'].empty_label = "-- Select Category (or leave blank for AI) --"


class CategoryForm(forms.ModelForm, BootstrapFormMixin):
    icon = forms.ChoiceField(choices=ICON_CHOICES, initial='bi-tag', required=False)

    class Meta:
        model = Category
        fields = ['name', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Groceries, Fuel, Subscriptions', 'id': 'id_category_name'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color', 'id': 'id_category_color', 'value': '#4f46e5'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_classes()


class CSVImportForm(forms.Form, BootstrapFormMixin):
    csv_file = forms.FileField(
        label="Bank Statement or Ledger CSV File",
        help_text="Accepts CSV with columns: Date, Amount, Description, and optionally Type, Category."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_classes()


class BudgetForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = Budget
        fields = ['category', 'limit_amount', 'month', 'year']
        widgets = {
            'limit_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '1', 'placeholder': '5000.00'}),
            'month': forms.NumberInput(attrs={'min': '1', 'max': '12', 'placeholder': '1-12'}),
            'year': forms.NumberInput(attrs={'min': '2020', 'max': '2030', 'placeholder': 'YYYY'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
        self.apply_bootstrap_classes()
        if 'category' in self.fields:
            self.fields['category'].empty_label = "-- Select Category to Cap --"


class SavingsGoalForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = SavingsGoal
        fields = ['goal_name', 'target_amount', 'saved_amount', 'deadline']
        widgets = {
            'goal_name': forms.TextInput(attrs={'placeholder': 'e.g. Emergency Fund, Goa Trip, New Laptop'}),
            'target_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '1', 'placeholder': '50000.00'}),
            'saved_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_classes()


class AssetForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = Asset
        fields = ['name', 'asset_type', 'amount']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. HDFC Savings, Zerodha Stocks, Emergency Cash'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'placeholder': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_classes()


class LiabilityForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = Liability
        fields = ['name', 'liability_type', 'amount']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. HDFC Credit Card, Student Loan, Home Mortgage'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'placeholder': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_classes()