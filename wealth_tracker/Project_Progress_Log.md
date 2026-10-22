# Smart Wealth Tracker and Budget Planner — Project Progress Log

**Tech Stack:** Python (Django) + MySQL + scikit-learn (AI/ML)
**Project folder (local):** `wealth_tracker/wealth_tracker/wealthtracker/` (this is where `manage.py` lives — always run commands from here)

---

## ✅ Module 1: Project Setup & Environment

**Commands used:**
```
python -m venv venv
venv\Scripts\activate
pip install django mysqlclient pillow django-chartjs pandas scikit-learn
django-admin startproject wealthtracker .
python manage.py startapp tracker
```

**Note:** Had to downgrade Django to work with local MySQL version:
```
pip uninstall django
pip install "django==5.1.5"
```

**`wealthtracker/settings.py` — key changes:**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tracker',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'wealth_tracker_db',
        'USER': 'root',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

**MySQL:**
```sql
CREATE DATABASE wealth_tracker_db;
```

**Verified:** `python manage.py migrate` + `python manage.py runserver` → Django rocket page loaded successfully.

---

## ✅ Module 2: Database Models

**File: `tracker/models.py`**
```python
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TRANSACTION_TYPE = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.amount} - {self.category}"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    limit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField()
    year = models.IntegerField()

    def __str__(self):
        return f"{self.category} - {self.limit_amount} ({self.month}/{self.year})"


class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    goal_name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    saved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField()

    def __str__(self):
        return self.goal_name
```

**File: `tracker/admin.py`**
```python
from django.contrib import admin
from .models import Category, Transaction, Budget, SavingsGoal

admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(Budget)
admin.site.register(SavingsGoal)
```

**Commands:**
```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

**Verified:** Logged into `/admin/` — Categorys, Transactions, Budgets, Savings goals all visible under "TRACKER" section.

---

## ✅ Module 3: User Authentication (Signup / Login / Logout)

**File: `tracker/forms.py`** (initial version — later extended in Module 4 & 5)
```python
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
```

**File: `tracker/templates/tracker/signup.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Sign Up - Smart Wealth Tracker</title>
</head>
<body>
    <h2>Sign Up</h2>
    <form method="POST">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Sign Up</button>
    </form>
    <p>Already have an account? <a href="{% url 'login' %}">Login here</a></p>
</body>
</html>
```

**File: `tracker/templates/tracker/login.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Login - Smart Wealth Tracker</title>
</head>
<body>
    <h2>Login</h2>
    <form method="POST">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Login</button>
    </form>
    <p>Don't have an account? <a href="{% url 'signup' %}">Sign up here</a></p>
</body>
</html>
```

**File: `wealthtracker/urls.py`**
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tracker.urls')),
]
```

**Verified:** Signup → auto-login → redirect to dashboard. Logout and re-login also tested successfully.

---

## ✅ Module 4: Transaction Management (Add / View / Delete)

**File: `tracker/forms.py`** (added to existing file)
```python
from .models import Transaction, Category, Budget

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'category', 'type', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
```

**File: `tracker/views.py`** (full file as of Module 5)
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .forms import SignUpForm, TransactionForm, CategoryForm, BudgetForm
from .models import Transaction, Category, Budget


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'tracker/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'tracker/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:10]
    total_income = sum(t.amount for t in Transaction.objects.filter(user=request.user, type='income'))
    total_expense = sum(t.amount for t in Transaction.objects.filter(user=request.user, type='expense'))
    balance = total_income - total_expense
    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def add_transaction_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm(user=request.user)
    return render(request, 'tracker/add_transaction.html', {'form': form})


@login_required
def transaction_list_view(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'tracker/transaction_list.html', {'transactions': transactions})


@login_required
def delete_transaction_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()
    return redirect('transaction_list')


@login_required
def add_category_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('add_transaction')
    else:
        form = CategoryForm()
    return render(request, 'tracker/add_category.html', {'form': form})


@login_required
def add_budget_view(request):
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


@login_required
def budget_list_view(request):
    budgets = Budget.objects.filter(user=request.user)
    budget_data = []
    for b in budgets:
        spent = Transaction.objects.filter(
            user=request.user, category=b.category, type='expense',
            date__month=b.month, date__year=b.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        percent = (spent / b.limit_amount * 100) if b.limit_amount > 0 else 0
        budget_data.append({
            'budget': b,
            'spent': spent,
            'percent': round(percent, 1),
            'exceeded': spent > b.limit_amount,
        })
    return render(request, 'tracker/budget_list.html', {'budget_data': budget_data})
```

**File: `tracker/templates/tracker/add_category.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Add Category - Smart Wealth Tracker</title>
</head>
<body>
    <h2>Add New Category</h2>
    <form method="POST">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Save Category</button>
    </form>
    <p><a href="{% url 'add_transaction' %}">Back to Add Transaction</a></p>
</body>
</html>
```

**File: `tracker/templates/tracker/add_transaction.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Add Transaction - Smart Wealth Tracker</title>
</head>
<body>
    <h2>Add Transaction</h2>

    {% if form.category.field.queryset.count == 0 %}
        <p style="color: red;">You have no categories yet. <a href="{% url 'add_category' %}">Add one first</a>.</p>
    {% endif %}

    <form method="POST">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Save Transaction</button>
    </form>

    <p><a href="{% url 'add_category' %}">+ Add New Category</a></p>
    <p><a href="{% url 'transaction_list' %}">View All Transactions</a></p>
    <p><a href="{% url 'dashboard' %}">Back to Dashboard</a></p>
</body>
</html>
```

**File: `tracker/templates/tracker/transaction_list.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>All Transactions - Smart Wealth Tracker</title>
</head>
<body>
    <h2>All Transactions</h2>
    <p><a href="{% url 'add_transaction' %}">+ Add New Transaction</a> | <a href="{% url 'dashboard' %}">Dashboard</a></p>

    <table border="1" cellpadding="8" cellspacing="0">
        <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Category</th>
            <th>Amount</th>
            <th>Description</th>
            <th>Action</th>
        </tr>
        {% for t in transactions %}
        <tr>
            <td>{{ t.date }}</td>
            <td>{{ t.type }}</td>
            <td>{{ t.category }}</td>
            <td>₹{{ t.amount }}</td>
            <td>{{ t.description }}</td>
            <td><a href="{% url 'delete_transaction' t.pk %}" onclick="return confirm('Delete this transaction?')">Delete</a></td>
        </tr>
        {% empty %}
        <tr><td colspan="6">No transactions yet.</td></tr>
        {% endfor %}
    </table>
</body>
</html>
```

**File: `tracker/templates/tracker/dashboard.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Smart Wealth Tracker</title>
</head>
<body>
    <h2>Welcome, {{ user.username }}!</h2>

    <h3>Summary</h3>
    <p>Total Income: ₹{{ total_income }}</p>
    <p>Total Expense: ₹{{ total_expense }}</p>
    <p><strong>Balance: ₹{{ balance }}</strong></p>

    <p>
        <a href="{% url 'add_transaction' %}">+ Add Transaction</a> |
        <a href="{% url 'transaction_list' %}">View All Transactions</a> |
        <a href="{% url 'budget_list' %}">Budgets</a> |
        <a href="{% url 'logout' %}">Logout</a>
    </p>

    <h3>Recent Transactions</h3>
    <table border="1" cellpadding="8" cellspacing="0">
        <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Category</th>
            <th>Amount</th>
            <th>Description</th>
        </tr>
        {% for t in transactions %}
        <tr>
            <td>{{ t.date }}</td>
            <td>{{ t.type }}</td>
            <td>{{ t.category }}</td>
            <td>₹{{ t.amount }}</td>
            <td>{{ t.description }}</td>
        </tr>
        {% empty %}
        <tr><td colspan="5">No transactions yet.</td></tr>
        {% endfor %}
    </table>
</body>
</html>
```

**Verified:** Added category "Food", added an expense transaction (₹200, Thali) and an income transaction (₹15000, salary) — both showed correctly on transaction list and dashboard. Delete link present and working.

---

## ✅ Module 5: Budget Planning

**File: `tracker/forms.py`** (added to existing file)
```python
class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'limit_amount', 'month', 'year']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
```
(views for budget already included in Module 4's `views.py` listing above — `add_budget_view` and `budget_list_view`)

**File: `tracker/templates/tracker/add_budget.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Add Budget - Smart Wealth Tracker</title>
</head>
<body>
    <h2>Set Monthly Budget</h2>

    {% if form.category.field.queryset.count == 0 %}
        <p style="color: red;">You have no categories yet. <a href="{% url 'add_category' %}">Add one first</a>.</p>
    {% endif %}

    <form method="POST">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Save Budget</button>
    </form>

    <p><a href="{% url 'budget_list' %}">View All Budgets</a></p>
    <p><a href="{% url 'dashboard' %}">Back to Dashboard</a></p>
</body>
</html>
```

**File: `tracker/templates/tracker/budget_list.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>My Budgets - Smart Wealth Tracker</title>
</head>
<body>
    <h2>My Budgets</h2>
    <p><a href="{% url 'add_budget' %}">+ Set New Budget</a> | <a href="{% url 'dashboard' %}">Dashboard</a></p>

    <table border="1" cellpadding="8" cellspacing="0">
        <tr>
            <th>Category</th>
            <th>Month/Year</th>
            <th>Limit</th>
            <th>Spent</th>
            <th>Progress</th>
            <th>Status</th>
        </tr>
        {% for item in budget_data %}
        <tr style="{% if item.exceeded %}background-color: #ffdddd;{% endif %}">
            <td>{{ item.budget.category }}</td>
            <td>{{ item.budget.month }}/{{ item.budget.year }}</td>
            <td>₹{{ item.budget.limit_amount }}</td>
            <td>₹{{ item.spent }}</td>
            <td>{{ item.percent }}%</td>
            <td>
                {% if item.exceeded %}
                    <strong style="color: red;">⚠ Exceeded!</strong>
                {% else %}
                    <span style="color: green;">On Track</span>
                {% endif %}
            </td>
        </tr>
        {% empty %}
        <tr><td colspan="6">No budgets set yet.</td></tr>
        {% endfor %}
    </table>
</body>
</html>
```

**File: `tracker/urls.py`** (final version so far)
```python
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('transactions/', views.transaction_list_view, name='transaction_list'),
    path('transactions/add/', views.add_transaction_view, name='add_transaction'),
    path('transactions/delete/<int:pk>/', views.delete_transaction_view, name='delete_transaction'),
    path('category/add/', views.add_category_view, name='add_category'),
    path('budget/add/', views.add_budget_view, name='add_budget'),
    path('budget/', views.budget_list_view, name='budget_list'),
]
```

**Verified:** Set a budget of ₹1000 for "Food" (9/2026) → budget list correctly showed Spent ₹200, Progress 20%, Status "On Track".

---

## ✅ Module 6: Dashboard Charts (Chart.js)

**Features:**
- Category-wise Expense Breakdown (Pie Chart)
- Monthly Income vs Expense Comparison (Bar Chart) for the last 6 months

**File: `tracker/views.py`** (added to `dashboard_view`):
```python
    # Module 6: Chart Data (Category Expenses Pie Chart)
    cat_expenses = (
        Transaction.objects.filter(user=request.user, type='expense')
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    pie_labels = [c['category__name'] or 'Uncategorized' for c in cat_expenses]
    pie_data = [float(c['total']) for c in cat_expenses]

    # Module 6: Chart Data (Monthly Income vs Expense Bar Chart - Last 6 Months)
    today = datetime.date.today()
    bar_labels = []
    bar_income = []
    bar_expense = []

    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        month_label = f"{calendar.month_abbr[m]} {y}"
        inc = Transaction.objects.filter(user=request.user, type='income', date__year=y, date__month=m).aggregate(total=Sum('amount'))['total'] or 0
        exp = Transaction.objects.filter(user=request.user, type='expense', date__year=y, date__month=m).aggregate(total=Sum('amount'))['total'] or 0
        bar_labels.append(month_label)
        bar_income.append(float(inc))
        bar_expense.append(float(exp))
```

**File: `tracker/templates/tracker/dashboard.html`** (added Chart.js script and canvas tags):
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<div style="display: flex; gap: 30px; flex-wrap: wrap;">
    <div style="width: 380px; border: 1px solid #ddd; padding: 15px;">
        <h4>Expense Breakdown by Category</h4>
        <canvas id="categoryPieChart" width="350" height="300"></canvas>
    </div>
    <div style="width: 500px; border: 1px solid #ddd; padding: 15px;">
        <h4>Monthly Income vs Expense (Last 6 Months)</h4>
        <canvas id="incomeExpenseBarChart" width="480" height="300"></canvas>
    </div>
</div>
```

**Verified:** Dashboard loads `categoryPieChart` showing Category slices and `incomeExpenseBarChart` showing Income vs. Expense bars.

---

## ✅ Module 7: AI/ML — Auto Expense Categorization + Expense Prediction

**Tech Stack:** Python `scikit-learn` (`MultinomialNB`, `CountVectorizer`, `LinearRegression`) + `pandas`

**File: `tracker/ai.py`**
- **Part A: Auto Categorization (Naive Bayes NLP):**
  Uses `CountVectorizer` and `MultinomialNB` trained on a comprehensive seed dataset of merchant/financial descriptions (Food, Transportation, Shopping, Utilities, Entertainment, Healthcare, Rent, Salary), dynamically augmented by user-entered transactions.
  Function: `predict_category(description, user=None)`
- **Part B: Expense Prediction (Linear Regression & pandas):**
  Uses `pandas` DataFrame to group monthly totals and fits `LinearRegression()` to forecast next month's total spending and daily velocity.
  Compares against active budget limits to flag overrun warnings.
  Function: `predict_expenses(user)`

**File: `tracker/templates/tracker/add_transaction.html`**
- Added live AI auto-predict button and suggestion endpoint `/api/predict-category/?desc=...`.
- If category is left blank, backend automatically assigns the predicted category on save.

**File: `tracker/templates/tracker/ai_insights.html`**
- Displays predicted next month expenses, daily spending velocity, projected month-end spend, and budget overrun risk.
- Interactive testing tool to input any description and see real-time AI classification and confidence score.

**Verified:**
- Tested description `"Starbucks coffee"` -> predicted `"Food"` with 66.2% confidence.
- Linear regression forecast calculated next month's spending and daily rate cleanly.

---

## ✅ Module 8: Savings Goal Tracker

**File: `tracker/forms.py`**
```python
class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['goal_name', 'target_amount', 'saved_amount', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }
```

**File: `tracker/views.py`** (added views):
- `add_savings_goal_view`: Add a new savings goal.
- `savings_goal_list_view`: Displays all goals with target amount, saved amount, progress percentage, remaining balance, and deadline countdown.
- `delete_savings_goal_view`: Delete a savings goal.
- `add_savings_contribution_view`: Add a deposit towards an existing goal.

**File: `tracker/templates/tracker/savings_goal_list.html`**
- Table with Goal Name, Target, Saved, Progress %, Remaining, Deadline, Status, and Action links.

**File: `tracker/templates/tracker/add_savings_goal.html`**
- Form to create a savings goal.

**File: `tracker/templates/tracker/add_savings_contribution.html`**
- Form to add a deposit towards a savings goal.

**File: `tracker/urls.py`** (final URLs):
```python
    path('', views.landing_view, name='landing'),
    path('home/', views.landing_view, name='home'),
    path('goals/', views.savings_goal_list_view, name='savings_goal_list'),
    path('goals/add/', views.add_savings_goal_view, name='add_savings_goal'),
    path('goals/delete/<int:pk>/', views.delete_savings_goal_view, name='delete_savings_goal'),
    path('goals/contribute/<int:pk>/', views.add_savings_contribution_view, name='add_savings_contribution'),
    path('ai/', views.ai_insights_view, name='ai_insights'),
    path('api/predict-category/', views.predict_category_api, name='predict_category_api'),
```

**Verified:** Created goal "Emergency Fund" (target ₹50,000, initial ₹10,000, deadline 2026-12-31); added ₹5,000 deposit -> saved amount updated to ₹15,000 (30% progress); verified dashboard widget and goals list.

---

## 🚀 How to Run the Project
1. Open terminal and navigate to the project directory:
   ```cmd
   cd wealth_tracker\wealth_tracker\wealthtracker
   ```
2. Activate virtual environment:
   ```cmd
   ..\venv\Scripts\activate
   ```
3. Run the Django development server:
   ```cmd
   python manage.py runserver
   ```
4. Open your browser at: **`http://127.0.0.1:8000/`**
5. Log in with user `shadow` (password: `shadow123`) or sign up a new account.

---

## Known Issues Fixed Along the Way (for reference)
- Nested folder confusion (`wealth_tracker\wealth_tracker\...`) — always `cd` into the folder containing `manage.py`.
- MySQL terminal login error (`caching_sha2_password` plugin missing) — used MySQL Workbench instead.
- `ImproperlyConfigured: Application labels aren't unique, duplicates: admin` — caused by `'django.contrib.admin'` duplicated in `INSTALLED_APPS`.
- `ModuleNotFoundError: No module named 'tracker'` — happened because `'tracker'` was in `INSTALLED_APPS` before the app was created via `startapp`.
- `NotSupportedError: MySQL 8.4 or later is required` — fixed by downgrading Django to 5.1.5.
- `CSS styling missing / unstyled plain HTML` — configured `STATIC_URL = '/static/'` and `STATICFILES_DIRS = [BASE_DIR / 'static']` in `settings.py`, created comprehensive `static/css/style.css` design system with navigation header, card components, form controls, progress bars, and unified `base.html` template.

---

## 🔒 Module 9: AI Feature Visibility Flag (Hiding AI on Website)
- **Goal:** Hide all AI/ML references, banners, navigation links, and sandbox widgets from the public website and UI, while preserving all underlying backend models, services, and algorithms intact so they can be re-enabled effortlessly later.
- **Implementation:**
  - Added `SHOW_AI_FEATURES = False` in `wealthtracker/settings.py`.
  - Created global template context processor in `tracker/context_processors.py` injecting `SHOW_AI_FEATURES`.
  - Updated all templates (`base.html`, `dashboard.html`, `landing.html`, `login.html`, `signup.html`, `add_transaction.html`, `transaction_list.html`, `import_transactions.html`) to conditionally render AI cards, badges, and copy.
  - Direct visits to `/ai/` cleanly redirect to `/dashboard/` when `SHOW_AI_FEATURES` is `False`.
  - **To Re-Enable AI in the Future:** Change `SHOW_AI_FEATURES = True` in `wealthtracker/settings.py`.




