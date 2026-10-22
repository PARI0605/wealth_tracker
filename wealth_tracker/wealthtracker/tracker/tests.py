import datetime
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from tracker.models import Category, Transaction, Budget, SavingsGoal, Asset, Liability
from tracker.services import (
    get_financial_summary,
    get_category_expense_breakdown,
    get_cash_flow_trend,
    get_dashboard_context,
    get_user_budget_overview,
    check_budget_status,
    get_user_goals_overview,
    contribute_to_goal,
    get_net_worth_summary,
)
from tracker.ai import (
    predict_expenses,
    predict_category,
    detect_anomalies,
    get_transaction_anomaly_ids,
    generate_budget_recommendations,
    generate_financial_insights,
)
from django.core.management import call_command


class MultiTenantIsolationTests(TestCase):
    """
    Verifies Rule 1: Strict multi-tenant data isolation.
    User B must NEVER be able to see or delete User A's data.
    """
    def setUp(self):
        self.user_a = User.objects.create_user(username='usera', password='password123')
        self.user_b = User.objects.create_user(username='userb', password='password123')

        self.cat_a = Category.objects.create(name='Food A', user=self.user_a)
        self.cat_b = Category.objects.create(name='Food B', user=self.user_b)

        self.tx_a = Transaction.objects.create(
            user=self.user_a,
            amount=Decimal('450.00'),
            category=self.cat_a,
            type='expense',
            description='Secret Lunch User A',
            date=datetime.date.today()
        )

        self.client_b = Client()
        self.client_b.login(username='userb', password='password123')

    def test_user_b_cannot_see_user_a_transactions(self):
        resp = self.client_b.get(reverse('transaction_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'Secret Lunch User A')

    def test_user_b_cannot_delete_user_a_transaction(self):
        resp = self.client_b.get(reverse('delete_transaction', args=[self.tx_a.pk]))
        self.assertEqual(resp.status_code, 404)
        # Verify transaction still exists in DB
        self.assertTrue(Transaction.objects.filter(pk=self.tx_a.pk).exists())


class DashboardServiceTests(TestCase):
    """
    Verifies Rule 2: Pure Decimal financial aggregation in dashboard_service.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='finance_user', password='password123')
        self.cat = Category.objects.create(name='Salary & Dining', user=self.user)

        Transaction.objects.create(
            user=self.user,
            amount=Decimal('50000.00'),
            category=self.cat,
            type='income',
            description='Monthly Salary',
            date=datetime.date.today()
        )
        Transaction.objects.create(
            user=self.user,
            amount=Decimal('12500.50'),
            category=self.cat,
            type='expense',
            description='Rent & Groceries',
            date=datetime.date.today()
        )

    def test_financial_summary_decimals(self):
        summary = get_financial_summary(self.user)
        self.assertEqual(summary['total_income'], Decimal('50000.00'))
        self.assertEqual(summary['total_expense'], Decimal('12500.50'))
        self.assertEqual(summary['balance'], Decimal('37499.50'))

    def test_dashboard_context(self):
        ctx = get_dashboard_context(self.user)
        self.assertEqual(ctx['total_income'], Decimal('50000.00'))
        self.assertEqual(ctx['total_expense'], Decimal('12500.50'))
        self.assertIn('pie_labels', ctx)
        self.assertIn('bar_income', ctx)


class BudgetServiceTests(TestCase):
    """
    Verifies spending thresholds, caution status (>80%), and overrun alerts in budget_service.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='budget_user', password='password123')
        self.cat = Category.objects.create(name='Groceries', user=self.user)
        today = datetime.date.today()

        self.budget = Budget.objects.create(
            user=self.user,
            category=self.cat,
            limit_amount=Decimal('10000.00'),
            month=today.month,
            year=today.year
        )

    def test_budget_caution_threshold(self):
        today = datetime.date.today()
        # Spend 85% of 10000 = 8500
        Transaction.objects.create(
            user=self.user,
            category=self.cat,
            amount=Decimal('8500.00'),
            type='expense',
            description='Supermarket',
            date=today
        )

        overview = get_user_budget_overview(self.user, month=today.month, year=today.year)
        self.assertEqual(len(overview), 1)
        item = overview[0]
        self.assertEqual(item['percent'], 85)
        self.assertTrue(item['is_caution'])
        self.assertFalse(item['exceeded'])
        self.assertEqual(item['status'], 'caution')

    def test_budget_exceeded_threshold(self):
        today = datetime.date.today()
        # Spend 11000 (> 10000 limit)
        Transaction.objects.create(
            user=self.user,
            category=self.cat,
            amount=Decimal('11000.00'),
            type='expense',
            description='Costly Groceries',
            date=today
        )

        overview = get_user_budget_overview(self.user, month=today.month, year=today.year)
        item = overview[0]
        self.assertEqual(item['percent'], 110)
        self.assertTrue(item['exceeded'])
        self.assertEqual(item['status'], 'exceeded')
        self.assertEqual(item['overrun'], Decimal('1000.00'))


class GoalServiceTests(TestCase):
    """
    Verifies goal progress percentage, countdowns, and atomic deposits.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='goal_user', password='password123')
        self.deadline = datetime.date.today() + datetime.timedelta(days=60)
        self.goal = SavingsGoal.objects.create(
            user=self.user,
            goal_name='Emergency Fund',
            target_amount=Decimal('100000.00'),
            saved_amount=Decimal('20000.00'),
            deadline=self.deadline
        )

    def test_goal_overview_and_deposit(self):
        overview = get_user_goals_overview(self.user)
        self.assertEqual(len(overview), 1)
        item = overview[0]
        self.assertEqual(item['percent'], 20)
        self.assertEqual(item['remaining'], Decimal('80000.00'))
        self.assertFalse(item['is_completed'])

        # Contribute 30000
        goal, new_total, new_pct, is_done = contribute_to_goal(self.user, self.goal.pk, Decimal('30000.00'))
        self.assertEqual(new_total, Decimal('50000.00'))
        self.assertEqual(new_pct, 50)
        self.assertFalse(is_done)


class WealthServiceTests(TestCase):
    """
    Verifies Net Worth calculation: Net Worth = Total Assets - Total Liabilities.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='wealth_user', password='password123')

        Asset.objects.create(
            user=self.user,
            name='Bank Balance',
            asset_type='bank',
            amount=Decimal('250000.00')
        )
        Asset.objects.create(
            user=self.user,
            name='Mutual Funds',
            asset_type='investment',
            amount=Decimal('150000.00')
        )

        Liability.objects.create(
            user=self.user,
            name='Credit Card Due',
            liability_type='credit_card',
            amount=Decimal('40000.00')
        )

    def test_net_worth_calculation(self):
        summary = get_net_worth_summary(self.user)
        self.assertEqual(summary['total_assets'], Decimal('400000.00'))
        self.assertEqual(summary['total_liabilities'], Decimal('400000.00') - Decimal('360000.00'))
        self.assertEqual(summary['net_worth'], Decimal('360000.00'))


class MLColdStartTests(TestCase):
    """
    Verifies Rule 3: ML model fallbacks when a user has zero transaction history.
    """
    def setUp(self):
        self.fresh_user = User.objects.create_user(username='fresh_user', password='password123')

    def test_forecaster_fallback_on_empty_user(self):
        forecast = predict_expenses(self.fresh_user)
        self.assertIsNotNone(forecast)
        self.assertIn('next_month_pred', forecast)
        self.assertIn('trend_label', forecast)
        self.assertIn('advice', forecast)

    def test_categorizer_general_prediction(self):
        cat_name, confidence, matched = predict_category('Swiggy delivery', user=self.fresh_user)
        self.assertEqual(cat_name, 'Food')
        self.assertGreater(confidence, 0.0)


class EnhancedTransactionTests(TestCase):
    """
    Verifies Phase 3 features: Signals, Edit Transaction, CSV Export & Import, and Filtering.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='phase3_user', password='password123')
        self.client = Client()
        self.client.login(username='phase3_user', password='password123')

    def test_default_categories_signal_on_user_creation(self):
        # A new user should automatically have default categories created by the signal
        new_user = User.objects.create_user(username='new_signup', password='password123')
        cats = Category.objects.filter(user=new_user)
        self.assertEqual(cats.count(), 10)
        self.assertTrue(cats.filter(name='Food & Dining').exists())
        self.assertTrue(cats.filter(name='Salary & Income').exists())

    def test_edit_transaction(self):
        cat = Category.objects.filter(user=self.user).first()
        tx = Transaction.objects.create(
            user=self.user,
            amount=Decimal('500.00'),
            category=cat,
            type='expense',
            description='Original Lunch',
            date=datetime.date.today()
        )

        resp = self.client.post(reverse('edit_transaction', args=[tx.pk]), {
            'amount': '750.00',
            'type': 'expense',
            'category': cat.pk if cat else '',
            'description': 'Updated Dinner',
            'date': datetime.date.today().strftime('%Y-%m-%d'),
            'payment_method': 'Credit Card',
        })
        self.assertEqual(resp.status_code, 302)
        tx.refresh_from_db()
        self.assertEqual(tx.amount, Decimal('750.00'))
        self.assertEqual(tx.description, 'Updated Dinner')
        self.assertEqual(tx.payment_method, 'Credit Card')

    def test_export_csv(self):
        cat = Category.objects.filter(user=self.user).first()
        Transaction.objects.create(
            user=self.user,
            amount=Decimal('1200.00'),
            category=cat,
            type='expense',
            description='Export Test Entry',
            date=datetime.date.today()
        )
        resp = self.client.get(reverse('export_transactions_csv'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename=', resp['Content-Disposition'])
        content = resp.content.decode('utf-8')
        self.assertIn('Amount (INR)', content)
        self.assertIn('Export Test Entry', content)
        self.assertIn('1200.00', content)

    def test_import_csv(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        csv_data = (
            "Date,Amount,Description,Type,Category\n"
            "2026-10-10,350.00,Swiggy Burger,expense,Food & Dining\n"
            "2026-10-11,45000.00,Company Monthly Salary,income,Salary & Income\n"
        ).encode('utf-8')

        uploaded = SimpleUploadedFile("statement.csv", csv_data, content_type="text/csv")
        resp = self.client.post(reverse('import_transactions_csv'), {'csv_file': uploaded})
        self.assertEqual(resp.status_code, 302)

        # Check transactions created
        self.assertTrue(Transaction.objects.filter(user=self.user, description='Swiggy Burger').exists())
        salary_tx = Transaction.objects.filter(user=self.user, description='Company Monthly Salary').first()
        self.assertIsNotNone(salary_tx)
        self.assertEqual(salary_tx.type, 'income')
        self.assertEqual(salary_tx.amount, Decimal('45000.00'))

    def test_transaction_search_and_filters(self):
        cat = Category.objects.filter(user=self.user).first()
        Transaction.objects.create(
            user=self.user,
            amount=Decimal('100.00'),
            category=cat,
            type='expense',
            description='Starbucks Coffee',
            date=datetime.date(2026, 10, 1)
        )
        Transaction.objects.create(
            user=self.user,
            amount=Decimal('200.00'),
            category=cat,
            type='income',
            description='Freelance Project',
            date=datetime.date(2026, 10, 5)
        )

        # Search by keyword
        resp = self.client.get(reverse('transaction_list'), {'q': 'Starbucks'})
        self.assertContains(resp, 'Starbucks Coffee')
        self.assertNotContains(resp, 'Freelance Project')

        # Filter by type
        resp = self.client.get(reverse('transaction_list'), {'type': 'income'})
        self.assertContains(resp, 'Freelance Project')
        self.assertNotContains(resp, 'Starbucks Coffee')


class Phase4NetWorthModuleTests(TestCase):
    """
    Verifies Phase 4: Net Worth Module, Assets/Liabilities CRUD,
    debt-to-asset ratios, solvency diagnostics, and trajectory generation.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='networth_user', password='password123')
        self.other_user = User.objects.create_user(username='other_nw_user', password='password123')
        self.client = Client()
        self.client.login(username='networth_user', password='password123')

        self.asset = Asset.objects.create(
            user=self.user,
            name='Axis Mutual Fund',
            asset_type='investment',
            amount=Decimal('50000.00')
        )
        self.liability = Liability.objects.create(
            user=self.user,
            name='SBI Credit Card',
            liability_type='credit_card',
            amount=Decimal('10000.00')
        )

    def test_net_worth_view_renders(self):
        resp = self.client.get(reverse('net_worth'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Net Worth &amp; Balance Sheet')
        self.assertContains(resp, 'Axis Mutual Fund')
        self.assertContains(resp, 'SBI Credit Card')
        self.assertContains(resp, 'netWorthTrajectoryChart')
        self.assertContains(resp, 'assetAllocationChart')

    def test_add_asset(self):
        resp = self.client.post(reverse('add_asset'), {
            'name': 'HDFC Fixed Deposit',
            'asset_type': 'bank',
            'amount': '25000.00'
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        new_asset = Asset.objects.filter(user=self.user, name='HDFC Fixed Deposit').first()
        self.assertIsNotNone(new_asset)
        self.assertEqual(new_asset.amount, Decimal('25000.00'))

    def test_edit_asset(self):
        resp = self.client.post(reverse('edit_asset', args=[self.asset.pk]), {
            'name': 'Axis Mutual Fund - Growth',
            'asset_type': 'investment',
            'amount': '65000.00'
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.name, 'Axis Mutual Fund - Growth')
        self.assertEqual(self.asset.amount, Decimal('65000.00'))

    def test_delete_asset(self):
        resp = self.client.get(reverse('delete_asset', args=[self.asset.pk]), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Asset.objects.filter(pk=self.asset.pk).exists())

    def test_add_liability(self):
        resp = self.client.post(reverse('add_liability'), {
            'name': 'Car Loan EMI',
            'liability_type': 'loan',
            'amount': '150000.00'
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        new_debt = Liability.objects.filter(user=self.user, name='Car Loan EMI').first()
        self.assertIsNotNone(new_debt)
        self.assertEqual(new_debt.amount, Decimal('150000.00'))

    def test_edit_liability(self):
        resp = self.client.post(reverse('edit_liability', args=[self.liability.pk]), {
            'name': 'SBI Card Settled',
            'liability_type': 'credit_card',
            'amount': '5000.00'
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.liability.refresh_from_db()
        self.assertEqual(self.liability.amount, Decimal('5000.00'))

    def test_delete_liability(self):
        resp = self.client.get(reverse('delete_liability', args=[self.liability.pk]), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Liability.objects.filter(pk=self.liability.pk).exists())

    def test_multi_tenant_asset_isolation(self):
        # Client B cannot edit or delete user A's asset
        client_b = Client()
        client_b.login(username='other_nw_user', password='password123')

        resp_edit = client_b.get(reverse('edit_asset', args=[self.asset.pk]))
        self.assertEqual(resp_edit.status_code, 404)

        resp_del = client_b.get(reverse('delete_asset', args=[self.asset.pk]))
        self.assertEqual(resp_del.status_code, 404)
        self.assertTrue(Asset.objects.filter(pk=self.asset.pk).exists())

    def test_wealth_service_calculations(self):
        summary = get_net_worth_summary(self.user)
        self.assertEqual(summary['total_assets'], Decimal('50000.00'))
        self.assertEqual(summary['total_liabilities'], Decimal('10000.00'))
        self.assertEqual(summary['net_worth'], Decimal('40000.00'))
        self.assertEqual(summary['debt_to_asset_ratio'], Decimal('20.0'))
        self.assertEqual(len(summary['trajectory_labels']), 6)
        self.assertEqual(len(summary['trajectory_data']), 6)
        self.assertIn('investment', summary['assets'][0].asset_type)


class Phase5AdvancedMLTests(TestCase):
    """
    Verifies Phase 5: Advanced AI/ML Module:
    - Anomaly Detection (Z-Score + Isolation Forest)
    - AI Budget Recommendations (3-Month Trailing Moving Average)
    - Apply Budget Recommendation View (POST)
    - Plain-Language Financial Insights Engine
    - Management command train_ml_models
    """
    def setUp(self):
        self.user = User.objects.create_user(username='ai_user', password='password123')
        self.client = Client()
        self.client.login(username='ai_user', password='password123')

        self.cat_dining = Category.objects.create(name='Food & Dining', user=self.user)
        self.cat_shopping = Category.objects.create(name='Shopping', user=self.user)

        today = datetime.date.today()
        # Seed 5 normal dining transactions ~ 400-600
        for i in range(5):
            Transaction.objects.create(
                user=self.user,
                amount=Decimal('500.00'),
                category=self.cat_dining,
                type='expense',
                description=f'Dinner {i+1}',
                date=today - datetime.timedelta(days=i * 5)
            )

        # Seed 1 spike transaction of 15,000
        self.spike_tx = Transaction.objects.create(
            user=self.user,
            amount=Decimal('15000.00'),
            category=self.cat_dining,
            type='expense',
            description='Expensive Luxury Banquet Dinner',
            date=today
        )

    def test_anomaly_detection_flags_outlier(self):
        anomalies = detect_anomalies(self.user, threshold_z=2.0)
        self.assertGreaterEqual(len(anomalies), 1)
        flagged_tx = anomalies[0]
        self.assertEqual(flagged_tx['transaction'].pk, self.spike_tx.pk)
        self.assertGreaterEqual(flagged_tx['z_score'], 2.0)
        self.assertIn('higher than your average', flagged_tx['reason'])

        # Verify fast lookup helper
        anomaly_ids = get_transaction_anomaly_ids(self.user)
        self.assertIn(self.spike_tx.pk, anomaly_ids)

    def test_budget_recommendations_generation(self):
        recs = generate_budget_recommendations(self.user)
        self.assertGreaterEqual(len(recs), 1)
        dining_rec = next((r for r in recs if r['category'].pk == self.cat_dining.pk), None)
        self.assertIsNotNone(dining_rec)
        self.assertGreater(dining_rec['recommended_limit'], Decimal('0.00'))
        self.assertIn(dining_rec['action_type'], ['create', 'increase', 'decrease', 'maintain'])

    def test_apply_budget_recommendation_view(self):
        resp = self.client.post(reverse('apply_budget_recommendation'), {
            'category_id': self.cat_dining.pk,
            'amount': '6500.00'
        }, follow=True)
        self.assertEqual(resp.status_code, 200)

        today = datetime.date.today()
        b = Budget.objects.filter(user=self.user, category=self.cat_dining, month=today.month, year=today.year).first()
        self.assertIsNotNone(b)
        self.assertEqual(b.limit_amount, Decimal('6500.00'))

    def test_plain_language_financial_insights(self):
        # Add income to trigger savings rate insight
        Transaction.objects.create(
            user=self.user,
            amount=Decimal('50000.00'),
            category=None,
            type='income',
            description='Salary Credit',
            date=datetime.date.today()
        )
        insights = generate_financial_insights(self.user)
        self.assertIsInstance(insights, list)
        self.assertGreaterEqual(len(insights), 1)
        first_insight = insights[0]
        self.assertIn('title', first_insight)
        self.assertIn('body', first_insight)
        self.assertIn('type', first_insight)

    def test_train_ml_models_command(self):
        call_command('train_ml_models')
        from django.conf import settings
        model_path = settings.BASE_DIR / 'ml_models' / 'nlp_categorizer.joblib'
        self.assertTrue(model_path.exists())

    def test_seed_demo_data_command(self):
        call_command('seed_demo_data', username='test_seed_user', clear=True)
        seed_user = User.objects.get(username='test_seed_user')
        self.assertGreater(Transaction.objects.filter(user=seed_user).count(), 50)
        self.assertGreater(Budget.objects.filter(user=seed_user).count(), 0)
        self.assertGreater(SavingsGoal.objects.filter(user=seed_user).count(), 0)
        self.assertGreater(Asset.objects.filter(user=seed_user).count(), 0)
        self.assertGreater(Liability.objects.filter(user=seed_user).count(), 0)



