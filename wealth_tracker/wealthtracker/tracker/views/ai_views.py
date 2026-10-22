import datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from tracker.models import Category, Budget
from tracker.ai import (
    predict_category,
    predict_expenses,
    detect_anomalies,
    generate_budget_recommendations,
    generate_financial_insights,
)


@login_required
def predict_category_api(request):
    """
    AJAX REST endpoint called during transaction creation to auto-predict
    category in real-time from description memo.
    """
    description = request.GET.get('desc', '')
    cat_name, confidence, matched_cat = predict_category(description, user=request.user)

    return JsonResponse({
        'predicted_category': cat_name or '',
        'confidence': confidence,
        'category_id': matched_cat.id if matched_cat else None,
        'category_name': matched_cat.name if matched_cat else (cat_name or ''),
    })


@login_required
def ai_insights_view(request):
    """
    Phase 5 & Module 7: Advanced AI & Machine Learning Hub.
    Renders:
      1. Linear Regression spending forecast & daily burn rate velocity.
      2. Anomaly Detection radar (Z-score + Isolation Forest).
      3. AI Smart Budget Recommendations (3-month moving average).
      4. Plain-language financial advisory cards.
      5. Interactive Naive Bayes NLP sandbox.
    """
    user = request.user
    ai_data = predict_expenses(user)
    anomalies = detect_anomalies(user, threshold_z=2.0)
    budget_recommendations = generate_budget_recommendations(user)
    financial_insights = generate_financial_insights(user)

    # Interactive Naive Bayes NLP Sandbox test evaluation
    test_result = None
    test_query = request.GET.get('query', '')
    if test_query:
        cat_name, confidence, matched = predict_category(test_query, user=user)
        test_result = {
            'query': test_query,
            'predicted_category': cat_name,
            'confidence': confidence,
            'matched_category': matched.name if matched else 'None (auto-mapped)',
        }

    return render(request, 'tracker/ai_insights.html', {
        'ai_data': ai_data,
        'anomalies': anomalies,
        'budget_recommendations': budget_recommendations,
        'financial_insights': financial_insights,
        'test_result': test_result,
        'test_query': test_query,
    })


@login_required
def apply_budget_recommendation_view(request):
    """
    One-click controller allowing a user to accept and apply an AI-recommended
    budget limit for the current active month.
    """
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        recommended_amount = request.POST.get('amount')

        category = get_object_or_404(Category, pk=category_id, user=request.user)

        try:
            limit_val = Decimal(str(recommended_amount))
            today = datetime.date.today()

            budget, created = Budget.objects.update_or_create(
                user=request.user,
                category=category,
                month=today.month,
                year=today.year,
                defaults={'limit_amount': limit_val}
            )

            action = "established" if created else "adjusted"
            messages.success(request, f"AI Recommended Budget {action}: ₹{limit_val:,.2f} allocated to '{category.name}'.")
        except Exception as e:
            messages.error(request, f"Failed to apply budget recommendation: {e}")

    return redirect('ai_insights')
