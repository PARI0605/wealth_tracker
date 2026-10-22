---
name: django-backend-conventions
description: Coding guidelines, architectural patterns, multi-tenant data isolation rules, and conventions for the Django backend in the Smart Wealth Tracker project.
---

# Django Backend Conventions & Architecture

## When to Use This Skill
Activate this skill whenever writing, refactoring, or reviewing any Django backend code, including models, views, services, forms, signals, and database migrations.

---

## Core Rules & Principles

### 1. Multi-Tenant Data Isolation (P0 Security Requirement)
- Every domain model must possess a foreign key to `django.contrib.auth.models.User` (`user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='...')`).
- **Never** execute an unscoped `Model.objects.all()`.
- Always scope queries explicitly: `Model.objects.filter(user=request.user)`.
- When fetching a single object by ID, always enforce user ownership:
  ```python
  obj = get_object_or_404(Model, pk=pk, user=request.user)
  ```

### 2. Fat-Service / Thin-View Pattern
- **Views (`tracker/views/`):** Thin controllers handling HTTP requests, form binding, calling services, and returning template renders or JsonResponse. Views should be under 50 lines.
- **Services (`tracker/services/`):** Pure Python business logic functions that perform arithmetic, aggregations, goal projections, and rule checks. Services must accept `user` as their first parameter.

### 3. Financial Exactness with Decimal
- Never store or calculate money using `float`.
- Use `models.DecimalField(max_digits=10, decimal_places=2)` in models.
- In Python code, import and use `from decimal import Decimal`.
- Always validate positive amounts: `amount > Decimal('0.00')`.

### 4. Database Aggregations over Python Loops
- Compute sums, counts, and averages using database aggregation:
  ```python
  from django.db.models import Sum
  total = Transaction.objects.filter(user=user, type='expense').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
  ```
- Use `TruncMonth` for grouping by calendar month.

### 5. Form Validation Discipline
- Always inherit from `forms.ModelForm` or `forms.Form`.
- Explicitly scope related querysets in `__init__`:
  ```python
  def __init__(self, *args, **kwargs):
      user = kwargs.pop('user', None)
      super().__init__(*args, **kwargs)
      if user:
          self.fields['category'].queryset = Category.objects.filter(user=user)
  ```

### 6. Migrations Discipline
- Never modify existing database columns or table names destructively without a migration plan.
- After every model change, run:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  python manage.py check
  ```
