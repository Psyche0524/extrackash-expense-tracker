from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.debts.models import Debt
from apps.investments.models import Investment
from apps.planning.models import Budget, Contribution, Goal
from apps.transactions.models import Transaction
from apps.wallets.models import Account

EMAIL = 'demo@example.test'
PASSWORD = 'local-dev-squirrel-77'  # local development only


class Command(BaseCommand):
    help = f'Create (or reset) a demo account with sample data. Log in as {EMAIL} / {PASSWORD}.'

    def handle(self, *args, **options):
        User.objects.filter(username=EMAIL).delete()
        u = User.objects.create_user(EMAIL, EMAIL, PASSWORD, first_name='Alex')
        bpi = Account.objects.create(user=u, provider='bpi', name='BPI Everyday', kind='bank', opening_balance=40000)
        gcash = Account.objects.create(user=u, provider='gcash', name='GCash', kind='wallet', opening_balance=22000)
        mari = Account.objects.create(user=u, provider='maribank', name='Maribank', kind='bank', opening_balance=15000,
                                      group='Savings', interest_rate=3.3)
        Account.objects.create(user=u, provider='gotyme', name='GoTyme', kind='bank', opening_balance=592, group='Savings')
        Account.objects.create(user=u, provider='cash', name='Wallet', kind='cash', opening_balance=8000)
        visa = Account.objects.create(user=u, provider='bpi', name='BPI Visa', kind='credit', credit_limit=50000, due_day=25)

        today = date.today()
        for kind, amount, desc, cat, acct, days_ago, note in [
            ('income', 62000, 'Monthly salary', 'salary', bpi, (today - today.replace(day=1)).days, ''),
            ('expense', 650, 'Wildflour', 'dining', bpi, 0, 'Lunch with Maya'),
            ('expense', 180, 'Grab', 'transport', gcash, 0, ''),
            ('expense', 2100, 'The Marketplace', 'groceries', bpi, 1, ''),
            ('expense', 549, 'Netflix', 'subscriptions', visa, 1, ''),
            ('expense', 4200, 'Uniqlo', 'shopping', visa, 3, ''),
        ]:
            Transaction.objects.create(user=u, kind=kind, amount=amount, description=desc, category=cat,
                                       account=acct, date=today - timedelta(days=days_ago), note=note)

        Transaction.objects.create(user=u, kind='income', amount=19.03, description='Interest', category='interest', account=mari)
        Transaction.objects.create(user=u, amount=350, description='Ramen', category='dining', account=gcash,
                                   tags='japan, food', date=today - timedelta(days=2))

        for cat, limit, period in [('dining', 8000, 'monthly'), ('shopping', 5000, 'monthly'), ('transport', 600, 'weekly')]:
            Budget.objects.create(user=u, category=cat, limit=limit, period=period)
        u.planned.create(name='Spotify', amount=169, category='subscriptions', account=gcash, next_date=today + timedelta(days=8))
        u.planned.create(name='Rent', amount=8000, category='bills', account=bpi, next_date=today + timedelta(days=13))
        u.planned.create(kind='income', name='Monthly salary', amount=62000, category='salary', account=bpi,
                         next_date=(today.replace(day=1) + timedelta(days=32)).replace(day=1))
        u.debts.create(kind='receivable', name='Maya', total=1200, monthly=1200, account=gcash, note='Concert tickets')
        u.trips.create(name='Japan, slowly', start=today - timedelta(days=3), end=today + timedelta(days=4), budget=40000)
        fund = Goal.objects.create(user=u, name='Emergency fund', note='Your future safety net', target=60000)
        Contribution.objects.create(goal=fund, amount=24000, description='Monthly contribution')
        Goal.objects.create(user=u, name='Japan, slowly', note='A little adventure', target=40000, target_date=date(today.year + 1, 4, 1))
        Debt.objects.create(user=u, kind='installment', name='MacBook Air', total=30000, monthly=2500, paid=10000, account=visa, due_day=25)
        Debt.objects.create(user=u, kind='loan', name='Personal loan', total=36000, monthly=3000, paid=18000, account=bpi, note='0% family loan')
        Investment.objects.create(user=u, name='Global index fund', label='Long-term', invested=90000, value=96000)
        Investment.objects.create(user=u, name='Government bonds', label='Fixed income', invested=30000, value=30500)
        self.stdout.write(self.style.SUCCESS(f'Demo ready. Log in as {EMAIL} / {PASSWORD}'))
