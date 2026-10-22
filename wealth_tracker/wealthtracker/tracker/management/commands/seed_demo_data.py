import random
import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management import call_command

from tracker.models import Category, Transaction, Budget, SavingsGoal, Asset, Liability
from tracker.signals import seed_categories_for_existing_user


class Command(BaseCommand):
    help = "Seeds realistic 6-month Indian financial data for viva demonstrations and UI evaluations."

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='demo_user',
            help='Target username to populate demo data for (default: demo_user).'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing financial records for this user before seeding.'
        )

    def handle(self, *args, **options):
        username = options['username']
        clear_existing = options['clear']

        self.stdout.write(self.style.NOTICE(f"=== INITIALIZING DEMO DATA SEED PIPELINE FOR '{username}' ==="))

        # 1. Get or create user
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password('password123')
            user.email = f"{username}@wealthtracker.test"
            user.first_name = "Arjun"
            user.last_name = "Sharma"
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created new demo user '{username}' with password 'password123'."))
        else:
            self.stdout.write(f"Using existing user '{username}'.")

        # 2. Seed default categories
        seed_categories_for_existing_user(user)
        cats = {c.name.lower(): c for c in Category.objects.filter(user=user)}

        # Helper to get category by name
        def get_cat(key: str):
            for k, v in cats.items():
                if key.lower() in k:
                    return v
            return list(cats.values())[0]

        # 3. Clear existing if requested
        if clear_existing:
            Transaction.objects.filter(user=user).delete()
            Budget.objects.filter(user=user).delete()
            SavingsGoal.objects.filter(user=user).delete()
            Asset.objects.filter(user=user).delete()
            Liability.objects.filter(user=user).delete()
            self.stdout.write(self.style.WARNING("Cleared existing financial data for clean demo state."))

        # 4. Generate 6 Months of Realistic Transactions (May 2026 to Oct 2026)
        today = datetime.date.today()
        created_tx_count = 0

        # Recurring Monthly Salaries & Rents
        for i in range(5, -1, -1):
            # Compute month & year
            m = today.month - i
            y = today.year
            while m <= 0:
                m += 12
                y -= 1

            # 1st of month: Monthly Salary
            salary_date = datetime.date(y, m, 1)
            Transaction.objects.create(
                user=user,
                category=get_cat('Salary'),
                amount=Decimal('75000.00'),
                type='income',
                description='TCS Monthly Corporate Salary',
                payment_method='Net Banking',
                date=salary_date,
                is_recurring=True
            )
            created_tx_count += 1

            # 3rd of month: House Rent
            rent_date = datetime.date(y, m, 3)
            Transaction.objects.create(
                user=user,
                category=get_cat('Rent'),
                amount=Decimal('18500.00'),
                type='expense',
                description='2BHK Apartment Monthly Rent',
                payment_method='Net Banking',
                date=rent_date,
                is_recurring=True
            )
            created_tx_count += 1

            # 5th of month: BESCOM Electricity Bill
            elec_date = datetime.date(y, m, 5)
            Transaction.objects.create(
                user=user,
                category=get_cat('Utilities'),
                amount=Decimal(str(random.randint(1400, 2100))) + Decimal('0.50'),
                type='expense',
                description='BESCOM Power Electricity Bill',
                payment_method='UPI',
                date=elec_date,
                is_recurring=True
            )
            created_tx_count += 1

            # 7th of month: Airtel Fiber Broadband
            wifi_date = datetime.date(y, m, 7)
            Transaction.objects.create(
                user=user,
                category=get_cat('Utilities'),
                amount=Decimal('1178.82'),
                type='expense',
                description='Airtel Xstream Fiber WiFi Bill',
                payment_method='UPI',
                date=wifi_date,
                is_recurring=True
            )
            created_tx_count += 1

            # 10th of month: Netflix & Spotify OTT
            ott_date = datetime.date(y, m, 10)
            Transaction.objects.create(
                user=user,
                category=get_cat('Entertainment'),
                amount=Decimal('649.00'),
                type='expense',
                description='Netflix 4K Ultra HD Subscription',
                payment_method='Credit Card',
                date=ott_date,
                is_recurring=True
            )
            created_tx_count += 1

            # Weekly Groceries (4 times per month)
            for week in [8, 15, 22, 28]:
                day = min(week, 28)
                Transaction.objects.create(
                    user=user,
                    category=get_cat('Groceries'),
                    amount=Decimal(str(random.randint(1200, 2600))),
                    type='expense',
                    description=random.choice(['DMart Supermarket Weekly Grocery', 'Blinkit Milk & Vegetables', 'Zepto Household Essentials']),
                    payment_method='UPI',
                    date=datetime.date(y, m, day)
                )
                created_tx_count += 1

            # Food & Dining orders (4-6 per month)
            for fd_day in [4, 9, 14, 19, 24, 27]:
                if fd_day <= 28:
                    Transaction.objects.create(
                        user=user,
                        category=get_cat('Food'),
                        amount=Decimal(str(random.randint(280, 850))),
                        type='expense',
                        description=random.choice(['Swiggy Biryani Delivery', 'Zomato Pizza Feast', 'Starbucks Cold Brew Coffee', 'Dominos Cheese Pizza']),
                        payment_method='UPI',
                        date=datetime.date(y, m, fd_day)
                    )
                    created_tx_count += 1

            # Transportation (Uber, Fuel, Metro)
            for t_day in [6, 12, 18, 25]:
                if t_day <= 28:
                    Transaction.objects.create(
                        user=user,
                        category=get_cat('Transportation'),
                        amount=Decimal(str(random.randint(180, 650))),
                        type='expense',
                        description=random.choice(['Uber Cab to Office', 'Ola Auto Ride Home', 'Metro Card Recharge', 'Shell Petrol Fuel Refill']),
                        payment_method='UPI',
                        date=datetime.date(y, m, t_day)
                    )
                    created_tx_count += 1

            # Occasional Shopping & Healthcare
            if m % 2 == 0:
                Transaction.objects.create(
                    user=user,
                    category=get_cat('Shopping'),
                    amount=Decimal(str(random.randint(1800, 4200))),
                    type='expense',
                    description=random.choice(['Amazon Electronics Order', 'Myntra Fashion Sneakers', 'Zara Linen Shirt']),
                    payment_method='Credit Card',
                    date=datetime.date(y, m, 16)
                )
                created_tx_count += 1
            else:
                Transaction.objects.create(
                    user=user,
                    category=get_cat('Healthcare'),
                    amount=Decimal(str(random.randint(450, 1600))),
                    type='expense',
                    description='Apollo Pharmacy Tablets & Vitamins',
                    payment_method='Debit Card',
                    date=datetime.date(y, m, 17)
                )
                created_tx_count += 1

        # High-Value Statistical Anomaly to light up the AI Anomaly Radar!
        Transaction.objects.create(
            user=user,
            category=get_cat('Food'),
            amount=Decimal('18500.00'),
            type='expense',
            description='JW Marriott Grand 5-Star Anniversary Dinner',
            payment_method='Credit Card',
            date=today - datetime.timedelta(days=4)
        )
        created_tx_count += 1

        Transaction.objects.create(
            user=user,
            category=get_cat('Shopping'),
            amount=Decimal('42000.00'),
            type='expense',
            description='Sony Bravia 4K Smart TV Purchase',
            payment_method='Credit Card',
            date=today - datetime.timedelta(days=12)
        )
        created_tx_count += 1

        self.stdout.write(self.style.SUCCESS(f"Generated {created_tx_count} realistic historical transactions spanning 6 months."))

        # 5. Seed Monthly Budgets for the Current Month
        budget_seeds = [
            ('Food', Decimal('10000.00')),
            ('Groceries', Decimal('9000.00')),
            ('Transportation', Decimal('4000.00')),
            ('Entertainment', Decimal('2500.00')),
            ('Shopping', Decimal('6000.00')),
        ]
        for cname, lim in budget_seeds:
            c = get_cat(cname)
            Budget.objects.update_or_create(
                user=user,
                category=c,
                month=today.month,
                year=today.year,
                defaults={'limit_amount': lim}
            )
        self.stdout.write(self.style.SUCCESS("Configured 5 active monthly budgets for the current cycle."))

        # 6. Seed Savings Goals
        SavingsGoal.objects.update_or_create(
            user=user,
            goal_name='Emergency Contingency Fund',
            defaults={
                'target_amount': Decimal('200000.00'),
                'saved_amount': Decimal('145000.00'),
                'deadline': today + datetime.timedelta(days=120)
            }
        )
        SavingsGoal.objects.update_or_create(
            user=user,
            goal_name='Goa Year-End Beach Vacation',
            defaults={
                'target_amount': Decimal('35000.00'),
                'saved_amount': Decimal('24500.00'),
                'deadline': today + datetime.timedelta(days=45)
            }
        )
        SavingsGoal.objects.update_or_create(
            user=user,
            goal_name='MacBook Pro M3 Fund',
            defaults={
                'target_amount': Decimal('85000.00'),
                'saved_amount': Decimal('85000.00'),  # 100% completed milestone!
                'deadline': today + datetime.timedelta(days=15)
            }
        )
        self.stdout.write(self.style.SUCCESS("Configured 3 savings goals (Emergency Fund, Goa Trip, and 100% Completed Laptop)."))

        # 7. Seed Net Worth Holdings (Positive Assets & Outstanding Liabilities)
        Asset.objects.update_or_create(
            user=user,
            name='HDFC Salary & Savings Account',
            defaults={'asset_type': 'bank', 'amount': Decimal('165000.00')}
        )
        Asset.objects.update_or_create(
            user=user,
            name='Zerodha Nifty 50 Index Portfolio',
            defaults={'asset_type': 'investment', 'amount': Decimal('320000.00')}
        )
        Asset.objects.update_or_create(
            user=user,
            name='Sovereign Gold Bonds (Tranche IV)',
            defaults={'asset_type': 'gold', 'amount': Decimal('95000.00')}
        )
        Asset.objects.update_or_create(
            user=user,
            name='Liquid Emergency Cash in Hand',
            defaults={'asset_type': 'cash', 'amount': Decimal('20000.00')}
        )

        Liability.objects.update_or_create(
            user=user,
            name='HDFC Regalia Credit Card Due',
            defaults={'liability_type': 'credit_card', 'amount': Decimal('14200.00')}
        )
        Liability.objects.update_or_create(
            user=user,
            name='SBI Higher Education Loan',
            defaults={'liability_type': 'loan', 'amount': Decimal('110000.00')}
        )
        self.stdout.write(self.style.SUCCESS("Configured 4 positive assets (INR 6,00,000) and 2 liabilities (INR 1,24,200)."))

        # 8. Train & Serialize ML Models with newly seeded transactions
        self.stdout.write(self.style.NOTICE("Triggering train_ml_models pipeline to sync NLP weights..."))
        call_command('train_ml_models')

        self.stdout.write(self.style.SUCCESS(
            "\n=======================================================\n"
            " DEMO DATA SEEDED SUCCESSFULLY FOR VIVA PRESENTATION! \n"
            "=======================================================\n"
            f"  Username    : {username}\n"
            f"  Password    : password123\n"
            f"  Dashboard   : http://127.0.0.1:8000/dashboard/\n"
            f"  Net Worth   : http://127.0.0.1:8000/net-worth/\n"
            f"  AI Hub      : http://127.0.0.1:8000/ai/\n"
            "======================================================="
        ))
