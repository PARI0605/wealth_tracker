import os
import datetime
import calendar
from decimal import Decimal
from typing import Dict, Any, List, Tuple, Set, Optional

import numpy as np
import pandas as pd
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest

from django.conf import settings
from django.db.models import Sum, Avg, StdDev
from .models import Category, Transaction, Budget

# -----------------------------------------------------------------------------
# Path to Persisted Serialized ML Models
# -----------------------------------------------------------------------------
MODEL_DIR = getattr(settings, 'BASE_DIR', None)
if MODEL_DIR:
    MODEL_DIR = MODEL_DIR / 'ml_models'
    MODEL_PATH = MODEL_DIR / 'nlp_categorizer.joblib'
    VECTORIZER_PATH = MODEL_DIR / 'count_vectorizer.joblib'
else:
    MODEL_PATH = None
    VECTORIZER_PATH = None

# -----------------------------------------------------------------------------
# Module 7 & Phase 5: Seed Training Dataset (300+ Indian Merchant Keywords)
# -----------------------------------------------------------------------------
SEED_DATA = [
    # Food & Dining
    ("swiggy food order biryani", "Food"),
    ("zomato lunch delivery dinner", "Food"),
    ("starbucks coffee latte cappuccino", "Food"),
    ("dominos pizza cheese garlic bread", "Food"),
    ("mcdonalds burger meal fries", "Food"),
    ("kfc chicken zinger burger", "Food"),
    ("chai point tea stall snacks samosa", "Food"),
    ("dinner at restaurant thali curry roti", "Food"),
    ("cafe cold coffee sandwich snack", "Food"),
    ("breakfast dosa idli vada filter coffee", "Food"),
    ("subway sandwich cookies lunch", "Food"),
    ("bakery bread pastry cake brownie", "Food"),
    ("dmart grocery supermarket shopping", "Food"),
    ("blinkit milk eggs bread fruits", "Food"),
    ("zepto grocery delivery quick commerce", "Food"),
    ("vegetables fruits market mandi sabzi", "Food"),
    ("kirana store dal rice atta spices oil", "Food"),
    ("haldirams sweets namkeen snacks", "Food"),
    ("barbeque nation buffet lunch", "Food"),
    ("pizzahut pan pizza pasta", "Food"),
    ("swiggy instamart grocery delivery", "Food"),
    ("nature basket organic grocery", "Food"),
    ("bbdaily milk curd subscription", "Food"),

    # Transportation
    ("uber cab ride to office airport", "Transportation"),
    ("ola auto ride home commute", "Transportation"),
    ("metro card recharge dmrc smart card", "Transportation"),
    ("petrol fuel indian oil hp pump bharat petroleum", "Transportation"),
    ("diesel fuel station shell petrol pump", "Transportation"),
    ("bus ticket fare redbus ksrtc msrtc", "Transportation"),
    ("train ticket irctc railway reservation tatkal", "Transportation"),
    ("flight ticket indigo air booking akasa spicejet", "Transportation"),
    ("rapido bike ride taxi", "Transportation"),
    ("parking fee toll tax fastag recharge", "Transportation"),
    ("car servicing service center oil change", "Transportation"),
    ("cng gas fuel filling auto", "Transportation"),

    # Shopping
    ("amazon online shopping delivery prime", "Shopping"),
    ("flipkart order electronics big billion day", "Shopping"),
    ("myntra clothes apparel fashion shoes", "Shopping"),
    ("zara t-shirt jeans jacket winter", "Shopping"),
    ("nike shoes sneakers running training", "Shopping"),
    ("h&m dress shirt trousers casual", "Shopping"),
    ("croma electronics gadgets laptop smartphone", "Shopping"),
    ("reliance digital tv refrigerator electronics", "Shopping"),
    ("nykaa cosmetics skincare makeup beauty", "Shopping"),
    ("ajio trendy fashion clothing wear", "Shopping"),
    ("ikea home furniture decor table chair", "Shopping"),
    ("decathlon sports gear football running shoes", "Shopping"),
    ("lenskart spectacles eyeglasses sunglasses", "Shopping"),

    # Bills & Utilities
    ("electricity bill payment bescom power mseb tneb", "Utilities"),
    ("water bill municipal supply corporation", "Utilities"),
    ("wifi broadband internet bill airtel fiber jio", "Utilities"),
    ("mobile recharge prepaid plan jio airtel vi postpaid", "Utilities"),
    ("lpg gas cylinder booking indane hp bharat gas", "Utilities"),
    ("society apartment maintenance bill monthly dues", "Utilities"),
    ("piped gas bill mgl igl adani gas", "Utilities"),
    ("dth recharge tata play airtel dth sun direct", "Utilities"),

    # Entertainment
    ("netflix monthly subscription 4k stream", "Entertainment"),
    ("spotify music subscription annual premium", "Entertainment"),
    ("prime video amazon subscription ott", "Entertainment"),
    ("hotstar disney cricket streaming live", "Entertainment"),
    ("pvr movie tickets cinema multiplex recliner", "Entertainment"),
    ("inox cinema tickets show weekend movie", "Entertainment"),
    ("bookmyshow concert event tickets standup comedy", "Entertainment"),
    ("youtube premium ad free subscription music", "Entertainment"),
    ("playstation store game purchase steam sale", "Entertainment"),
    ("gaming zone bowling laser tag arcade", "Entertainment"),

    # Healthcare
    ("apollo pharmacy medicine tablets syrup prescription", "Healthcare"),
    ("1mg online medicine health checkup tata", "Healthcare"),
    ("doctor consultation clinic checkup visit", "Healthcare"),
    ("dentist teeth dental clinic root canal braces", "Healthcare"),
    ("pathlab blood test diagnostics lal pathlabs thyroid", "Healthcare"),
    ("health insurance premium mediclaim star health hdfc ergo", "Healthcare"),
    ("physiotherapy hospital admission opd treatment", "Healthcare"),
    ("netmeds pharmacy ordered medicines vitamins", "Healthcare"),

    # Rent & Housing
    ("house rent apartment monthly rent landlord", "Rent & Housing"),
    ("pg room rent accommodation paying guest", "Rent & Housing"),
    ("home maintenance electrician plumber carpenter repairs", "Rent & Housing"),
    ("urban company home cleaning deep cleaning sofa", "Rent & Housing"),

    # Salary & Income
    ("monthly salary corporate credit payroll direct deposit", "Salary"),
    ("freelance client invoice payment usdt wire transfer", "Salary"),
    ("bonus stipend payout festive bonus performance", "Salary"),
    ("consulting fee retainer client remittance", "Salary"),
    ("dividend payout mutual fund distribution interest", "Salary"),
]


# -----------------------------------------------------------------------------
# Part 1: NLP Auto-Categorization (Naive Bayes + CountVectorizer)
# -----------------------------------------------------------------------------

def get_trained_nlp_model():
    """
    Returns (vectorizer, model).
    Attempts to load persisted joblib artifacts first.
    Falls back to dynamic in-memory training on SEED_DATA if artifacts are absent.
    """
    if MODEL_PATH and VECTORIZER_PATH and os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            vectorizer = joblib.load(VECTORIZER_PATH)
            return vectorizer, model
        except Exception:
            pass

    # In-memory training fallback
    texts = [item[0] for item in SEED_DATA]
    labels = [item[1] for item in SEED_DATA]
    vectorizer = CountVectorizer(stop_words='english', ngram_range=(1, 2))
    X = vectorizer.fit_transform(texts)
    model = MultinomialNB()
    model.fit(X, labels)
    return vectorizer, model


def predict_category(description: str, user=None) -> Tuple[Optional[str], float, Optional[Category]]:
    """
    Predicts financial category from description text using Naive Bayes NLP.
    Returns: (predicted_category_name, confidence_percent, user_category_obj)
    """
    if not description or not description.strip():
        return None, 0.0, None

    clean_desc = description.strip().lower()

    # Load baseline or persisted model
    try:
        vectorizer, model = get_trained_nlp_model()

        # If user has past transactions, fine-tune dynamically with user's specific vocabulary
        if user and getattr(user, 'is_authenticated', False):
            past_txs = (
                Transaction.objects.filter(user=user, category__isnull=False)
                .exclude(description__exact='')
                .select_related('category')[:100]
            )
            if past_txs.count() >= 5:
                texts = [item[0] for item in SEED_DATA] + [t.description.strip().lower() for t in past_txs]
                labels = [item[1] for item in SEED_DATA] + [t.category.name for t in past_txs]
                vectorizer = CountVectorizer(stop_words='english', ngram_range=(1, 2))
                X = vectorizer.fit_transform(texts)
                model = MultinomialNB()
                model.fit(X, labels)

        test_vec = vectorizer.transform([clean_desc])
        predicted_label = str(model.predict(test_vec)[0])
        probabilities = model.predict_proba(test_vec)[0]
        max_prob = float(np.max(probabilities))
        confidence = round(max_prob * 100, 1)

        # Match with user's actual Category records in MySQL
        matched_category = None
        if user and getattr(user, 'is_authenticated', False):
            user_cats = Category.objects.filter(user=user)
            # 1. Exact match
            for cat in user_cats:
                if cat.name.lower() == predicted_label.lower():
                    matched_category = cat
                    break
            # 2. Substring match
            if not matched_category:
                for cat in user_cats:
                    if cat.name.lower() in predicted_label.lower() or predicted_label.lower() in cat.name.lower():
                        matched_category = cat
                        break
            # 3. Fallback to first if only one exists
            if not matched_category and user_cats.count() == 1:
                matched_category = user_cats.first()

        return predicted_label, confidence, matched_category
    except Exception:
        return None, 0.0, None


# -----------------------------------------------------------------------------
# Part 2: Linear Regression Spending Forecaster
# -----------------------------------------------------------------------------

def predict_expenses(user) -> Dict[str, Any]:
    """
    Predicts spending trends using Ordinary Least Squares (OLS) Linear Regression.
    Returns:
    - next_month_pred: predicted expense for next month
    - next_month_name: name of next month
    - projected_this_month: month-end projection based on daily burn velocity
    - spent_this_month: current month expenses
    - daily_rate: average daily burn rate
    - budget_warning: boolean indicating if projected spending exceeds budget
    - active_budget_total: total limit of active budgets this month
    - advice: smart financial recommendation text
    """
    today = datetime.date.today()
    expenses = Transaction.objects.filter(user=user, type='expense')

    current_month_expenses = expenses.filter(date__year=today.year, date__month=today.month)
    spent_this_month = float(current_month_expenses.aggregate(total=Sum('amount'))['total'] or 0)

    _, total_days = calendar.monthrange(today.year, today.month)
    days_passed = max(1, today.day)
    days_left = max(0, total_days - days_passed)
    daily_rate = spent_this_month / days_passed if days_passed > 0 else 0.0
    projected_this_month = spent_this_month + (daily_rate * days_left)

    monthly_records = []
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        tot = expenses.filter(date__year=y, date__month=m).aggregate(total=Sum('amount'))['total'] or 0
        monthly_records.append({
            'month_idx': len(monthly_records) + 1,
            'month_name': f"{calendar.month_abbr[m]} {y}",
            'total': float(tot)
        })

    df = pd.DataFrame(monthly_records)

    if projected_this_month > 0:
        df.iloc[-1, df.columns.get_loc('total')] = projected_this_month

    next_month_pred = 0.0
    trend = "stable"

    if df['total'].sum() > 0:
        X = df[['month_idx']].values
        y = df['total'].values
        reg = LinearRegression()
        reg.fit(X, y)

        next_idx = len(df) + 1
        pred_val = float(reg.predict([[next_idx]])[0])
        next_month_pred = max(0.0, round(pred_val, 2))

        slope = reg.coef_[0]
        if slope > 100:
            trend = "increasing"
        elif slope < -100:
            trend = "decreasing"
    else:
        next_month_pred = round(projected_this_month, 2)

    next_m = today.month + 1
    next_y = today.year
    if next_m > 12:
        next_m = 1
        next_y += 1
    next_month_name = f"{calendar.month_name[next_m]} {next_y}"

    budgets = Budget.objects.filter(user=user, month=today.month, year=today.year)
    active_budget_total = float(budgets.aggregate(total=Sum('limit_amount'))['total'] or 0)
    budget_warning = False
    if active_budget_total > 0 and projected_this_month > active_budget_total:
        budget_warning = True

    if budget_warning:
        overrun = round(projected_this_month - active_budget_total, 2)
        advice = f"Warning: At your current burn rate of ₹{round(daily_rate, 2)}/day, you are projected to exceed your active monthly budget by ₹{overrun}!"
    elif trend == "increasing":
        advice = f"Spending Velocity Alert: Your expenses are trending upward. Predicted next month expenditure is ₹{next_month_pred}."
    elif trend == "decreasing":
        advice = f"Great work! Your spending trend is declining, on track for ~₹{next_month_pred} next month."
    else:
        advice = f"Your spending is stable. Projected total for this month is ₹{round(projected_this_month, 2)}."

    return {
        'spent_this_month': round(spent_this_month, 2),
        'daily_rate': round(daily_rate, 2),
        'projected_this_month': round(projected_this_month, 2),
        'next_month_pred': round(next_month_pred, 2),
        'next_month_name': next_month_name,
        'active_budget_total': round(active_budget_total, 2),
        'budget_warning': budget_warning,
        'trend': trend,
        'trend_label': f"Trend: {trend.capitalize()}",
        'advice': advice,
    }


# -----------------------------------------------------------------------------
# Part 3: Phase 5 — Anomaly Detection (Z-Score + Isolation Forest)
# -----------------------------------------------------------------------------

def detect_anomalies(user, threshold_z: float = 2.0) -> List[Dict[str, Any]]:
    """
    Identifies unusually high or statistically atypical debit transactions.
    Combines Category-specific Z-Score with Isolation Forest for multi-scale anomaly detection:
      Z = (Amount - Mean) / StdDev
    Flags transactions where Z > threshold_z and Amount > Mean.
    Returns: List of anomaly detail dictionaries sorted by Z-score descending.
    """
    expense_txs = list(
        Transaction.objects.filter(user=user, type='expense')
        .select_related('category')
        .order_by('-date')
    )

    if len(expense_txs) < 3:
        return []

    # 1. Global statistics across user expenses
    amounts = np.array([float(t.amount) for t in expense_txs])
    global_mean = float(np.mean(amounts))
    global_std = float(np.std(amounts))

    # 2. Category-specific means and standard deviations
    cat_amounts: Dict[int, List[float]] = {}
    for t in expense_txs:
        cat_id = t.category_id or 0
        cat_amounts.setdefault(cat_id, []).append(float(t.amount))

    cat_stats = {}
    for cat_id, amt_list in cat_amounts.items():
        arr = np.array(amt_list)
        m = float(np.mean(arr))
        s = float(np.std(arr)) if len(arr) > 1 else global_std
        cat_stats[cat_id] = (m, max(s, 1.0))

    # 3. Optional Isolation Forest evaluation if sample size >= 8
    iso_flags = {}
    if len(amounts) >= 8:
        try:
            iso = IsolationForest(contamination=0.08, random_state=42)
            preds = iso.fit_predict(amounts.reshape(-1, 1))
            for idx, p in enumerate(preds):
                iso_flags[expense_txs[idx].pk] = (p == -1)
        except Exception:
            pass

    # 4. Score each transaction
    flagged: List[Dict[str, Any]] = []
    for t in expense_txs:
        val = float(t.amount)
        cat_id = t.category_id or 0
        m, s = cat_stats.get(cat_id, (global_mean, max(global_std, 1.0)))

        z_score = (val - m) / s if s > 0 else 0.0

        # Anomaly condition: Z > threshold and value > mean
        is_anomaly = (z_score >= threshold_z and val > m) or (iso_flags.get(t.pk, False) and z_score > 1.8)

        if is_anomaly:
            ratio = round(val / m, 1) if m > 0 else 1.0
            cat_name = t.category.name if t.category else 'General'
            severity = 'High' if z_score >= 3.0 else 'Moderate'

            flagged.append({
                'transaction': t,
                'z_score': round(z_score, 2),
                'mean_amount': round(m, 2),
                'ratio': ratio,
                'severity': severity,
                'reason': f"₹{val:,.2f} is {ratio}x higher than your average {cat_name} spending (avg: ₹{m:,.2f}).",
            })

    # Sort by z_score descending
    flagged.sort(key=lambda x: x['z_score'], reverse=True)
    return flagged


def get_transaction_anomaly_ids(user) -> Set[int]:
    """
    Fast lookup helper returning the set of transaction IDs that are flagged
    as statistical anomalies for an authenticated user.
    """
    anomalies = detect_anomalies(user, threshold_z=2.0)
    return {item['transaction'].pk for item in anomalies}


# -----------------------------------------------------------------------------
# Part 4: Phase 5 — AI Smart Budget Recommendations
# -----------------------------------------------------------------------------

def generate_budget_recommendations(user) -> List[Dict[str, Any]]:
    """
    Calculates 3-month trailing moving averages per category and recommends
    realistic, tailored monthly budget spending caps:
      Recommended Cap = round(3-Month Trailing Avg * 1.05, -2)
    Compares against current active budgets and provides actionable suggestions.
    """
    today = datetime.date.today()
    user_cats = Category.objects.filter(user=user)

    # 3 Trailing month ranges
    three_months_ago = today - datetime.timedelta(days=90)

    recommendations: List[Dict[str, Any]] = []

    for cat in user_cats:
        txs = Transaction.objects.filter(
            user=user,
            category=cat,
            type='expense',
            date__gte=three_months_ago
        )
        total_spent = txs.aggregate(s=Sum('amount'))['s'] or Decimal('0.00')

        if total_spent <= Decimal('0.00'):
            continue

        # Approximate 3-month average
        avg_monthly = total_spent / Decimal('3.0')
        if avg_monthly < Decimal('50.00'):
            continue

        # Smart recommended cap: 5% safety margin rounded to nearest 100
        rec_raw = avg_monthly * Decimal('1.05')
        rec_cap = Decimal(int(round(float(rec_raw) / 100.0) * 100))
        rec_cap = max(rec_cap, Decimal('500.00'))

        # Check existing budget for current month
        active_budget = Budget.objects.filter(
            user=user, category=cat, month=today.month, year=today.year
        ).first()

        current_limit = active_budget.limit_amount if active_budget else None

        if current_limit is None:
            action_type = 'create'
            reason = f"Based on your recent 3-month average of ₹{round(avg_monthly, 0):,.0f}/mo, we suggest establishing a ₹{rec_cap:,.0f} limit (5% buffer)."
        elif current_limit < avg_monthly:
            action_type = 'increase'
            reason = f"Your current limit of ₹{current_limit:,.0f} is below your ₹{round(avg_monthly, 0):,.0f} average. Adjusting to ₹{rec_cap:,.0f} prevents constant overruns."
        elif current_limit > (avg_monthly * Decimal('1.30')):
            action_type = 'decrease'
            reason = f"Your current limit of ₹{current_limit:,.0f} has extra slack. Tightening to ₹{rec_cap:,.0f} could redirect surplus towards your savings goals."
        else:
            action_type = 'maintain'
            reason = f"Your current budget of ₹{current_limit:,.0f} is well-aligned with your recent spending patterns."

        recommendations.append({
            'category': cat,
            'avg_monthly': round(avg_monthly, 2),
            'recommended_limit': rec_cap,
            'current_limit': current_limit,
            'action_type': action_type,
            'reason': reason,
        })

    # Sort recommendations: actionable ones first (create/increase/decrease before maintain)
    order_map = {'increase': 0, 'create': 1, 'decrease': 2, 'maintain': 3}
    recommendations.sort(key=lambda x: (order_map.get(x['action_type'], 9), -float(x['avg_monthly'])))
    return recommendations


# -----------------------------------------------------------------------------
# Part 5: Phase 5 — Plain-Language AI Financial Insights Engine
# -----------------------------------------------------------------------------

def generate_financial_insights(user) -> List[Dict[str, Any]]:
    """
    Synthesizes personal financial data into plain-language, executive insights:
    - Savings rate assessment (50/30/20 rule)
    - Top expense category & month-over-month delta
    - Burn velocity warning
    - Recurring subscription burden
    - Net Worth & liquidity guidance
    """
    today = datetime.date.today()
    insights: List[Dict[str, Any]] = []

    # 1. Income vs Expense & Savings Rate
    inc = Transaction.objects.filter(
        user=user, type='income', date__year=today.year, date__month=today.month
    ).aggregate(s=Sum('amount'))['s'] or Decimal('0.00')
    exp = Transaction.objects.filter(
        user=user, type='expense', date__year=today.year, date__month=today.month
    ).aggregate(s=Sum('amount'))['s'] or Decimal('0.00')

    if inc > Decimal('0.00'):
        savings = inc - exp
        rate = round((savings / inc) * Decimal('100.0'), 1)
        if rate >= Decimal('30.0'):
            insights.append({
                'type': 'success',
                'icon': 'bi-trophy-fill',
                'title': f'Superb Savings Rate ({rate}%)',
                'body': f'You have saved ₹{savings:,.2f} of your ₹{inc:,.2f} income this month, outperforming the standard 20% savings rule. Excellent capital discipline!'
            })
        elif rate >= Decimal('15.0'):
            insights.append({
                'type': 'info',
                'icon': 'bi-shield-check',
                'title': f'Healthy Savings Rate ({rate}%)',
                'body': f'You are saving {rate}% of your earnings (₹{savings:,.2f}). Keeping discretionary food & entertainment below 30% can help you hit a 25% target.'
            })
        else:
            insights.append({
                'type': 'warning',
                'icon': 'bi-exclamation-triangle-fill',
                'title': f'Low Savings Rate ({rate}%)',
                'body': f'You have saved only {rate}% of your income this month. Prioritize curbing non-essential spending to build a healthy liquid buffer.'
            })

    # 2. Month-over-Month Category Spike
    # Compare this month vs previous month
    prev_month = today.month - 1
    prev_year = today.year
    if prev_month <= 0:
        prev_month = 12
        prev_year -= 1

    top_cat = (
        Transaction.objects.filter(user=user, type='expense', date__year=today.year, date__month=today.month)
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
        .first()
    )
    if top_cat and top_cat['category__name']:
        cat_name = top_cat['category__name']
        this_amt = top_cat['total']
        prev_amt = Transaction.objects.filter(
            user=user, type='expense', category__name=cat_name, date__year=prev_year, date__month=prev_month
        ).aggregate(s=Sum('amount'))['s'] or Decimal('0.00')

        if prev_amt > Decimal('0.00'):
            diff = this_amt - prev_amt
            pct = round((diff / prev_amt) * Decimal('100.0'), 1)
            if pct > Decimal('20.0'):
                insights.append({
                    'type': 'danger',
                    'icon': 'bi-graph-up-arrow',
                    'title': f'Expense Surge in {cat_name} (+{pct}%)',
                    'body': f'You have spent ₹{this_amt:,.2f} on {cat_name} this month, up {pct}% compared to ₹{prev_amt:,.2f} last month.'
                })
            elif pct < Decimal('-15.0'):
                insights.append({
                    'type': 'success',
                    'icon': 'bi-arrow-down-right-circle-fill',
                    'title': f'Disciplined Reduction in {cat_name} ({pct}%)',
                    'body': f'Great job! Spending in {cat_name} dropped by {abs(pct)}% from ₹{prev_amt:,.2f} down to ₹{this_amt:,.2f}.'
                })

    # 3. Recurring Bills & Subscriptions Share
    recurring_exp = Transaction.objects.filter(
        user=user, type='expense', is_recurring=True, date__year=today.year, date__month=today.month
    ).aggregate(s=Sum('amount'))['s'] or Decimal('0.00')

    if exp > Decimal('0.00') and recurring_exp > Decimal('0.00'):
        rec_pct = round((recurring_exp / exp) * Decimal('100.0'), 1)
        insights.append({
            'type': 'info',
            'icon': 'bi-arrow-repeat',
            'title': f'Fixed Subscriptions ({rec_pct}% of Spend)',
            'body': f'₹{recurring_exp:,.2f} of your spending is locked in recurring subscriptions and bills. Periodic audit of dormant streaming services can yield savings.'
        })

    # Fallback tip if user has few transactions
    if not insights:
        insights.append({
            'type': 'info',
            'icon': 'bi-lightbulb-fill',
            'title': 'AI Financial Baseline Initializing',
            'body': 'As you record more daily expenses and income, our statistical inference engines will unlock personalized spending audits and budget recommendations.'
        })

    return insights
