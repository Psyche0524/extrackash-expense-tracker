from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.debts.models import Debt
from apps.households.models import Household
from apps.investments.models import Investment
from apps.planning.models import Budget, Goal
from apps.transactions.models import Transaction
from apps.wallets.models import Account
from apps.core.templatetags.money import peso


def make_user(email='alex@example.com', name='Alex'):
    return User.objects.create_user(email, email, 'squirrel-cash-26', first_name=name)


class AuthTests(TestCase):
    def test_pages_need_login(self):
        for url in ['/', '/activity/', '/add/', '/plan/', '/explore/accounts/', '/settings/']:
            self.assertRedirects(self.client.get(url), f'/welcome/?next={url}')

    def test_signup_then_setup_first_account(self):
        response = self.client.post('/signup/', {
            'first_name': 'Alex', 'email': 'Alex@Example.com',
            'password1': 'squirrel-cash-26', 'password2': 'squirrel-cash-26',
        })
        self.assertRedirects(response, '/setup/')
        response = self.client.post('/setup/', {'provider': 'bpi', 'name': 'BPI Everyday', 'kind': 'bank', 'opening_balance': '54250'})
        self.assertRedirects(response, '/ready/')
        self.assertContains(self.client.get('/'), '<br>Alex')
        self.assertContains(self.client.get('/explore/accounts/'), '₱54,250.00')
        self.assertEqual(User.objects.get().username, 'alex@example.com')

    def test_duplicate_email_rejected(self):
        make_user()
        response = self.client.post('/signup/', {
            'first_name': 'A', 'email': 'ALEX@example.com',
            'password1': 'squirrel-cash-26', 'password2': 'squirrel-cash-26',
        })
        self.assertContains(response, 'already exists')

    def test_login_with_email_any_case_and_logout(self):
        make_user()
        response = self.client.post('/login/', {'username': 'ALEX@example.com', 'password': 'squirrel-cash-26'})
        self.assertRedirects(response, '/')
        self.assertRedirects(self.client.post('/logout/'), '/welcome/')

    def test_wrong_password_shows_error(self):
        make_user()
        response = self.client.post('/login/', {'username': 'alex@example.com', 'password': 'nope'})
        self.assertContains(response, 'Email or password is incorrect.')

    def test_delete_account_needs_typed_confirmation(self):
        user = make_user()
        self.client.force_login(user)
        self.client.post('/settings/delete/', {'confirm': 'yes'})
        self.assertTrue(User.objects.exists())
        self.assertRedirects(self.client.post('/settings/delete/', {'confirm': 'DELETE'}), '/welcome/')
        self.assertFalse(User.objects.exists())


class MoneyTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_login(self.user)
        self.bank = Account.objects.create(user=self.user, name='BPI', kind='bank', opening_balance=1000)
        self.gcash = Account.objects.create(user=self.user, name='GCash', kind='wallet', opening_balance=0)

    def add(self, **data):
        base = {'kind': 'expense', 'amount': '100', 'description': 'X', 'category': 'other',
                'account': self.bank.pk, 'date': '2026-11-17', 'note': ''}
        return self.client.post('/add/', {**base, **data})

    def test_peso_filter(self):
        self.assertEqual(peso(Decimal('1234.5')), '₱1,234.50')
        self.assertEqual(peso(-20), '−₱20.00')

    def test_income_expense_and_transfer_balances(self):
        self.add(kind='income', amount='500', category='salary')
        self.add(amount='200')
        self.client.post('/transfer/', {'account': self.bank.pk, 'to_account': self.gcash.pk, 'amount': '300', 'date': '2026-11-17'})
        self.bank.refresh_from_db()
        self.assertEqual(self.bank.balance, 1000)   # 1000 + 500 - 200 - 300
        self.assertEqual(self.gcash.balance, 300)
        self.assertEqual(self.client.get('/explore/accounts/').context['net'], 1300)  # own transfers don't change it

    def test_add_wallet_uses_provider_name_and_colour(self):
        self.client.post('/explore/accounts/new/', {'provider': 'gcash', 'name': '', 'kind': 'wallet', 'opening_balance': '545'})
        wallet = Account.objects.get(provider='gcash')
        self.assertEqual(wallet.name, 'GCash')
        page = self.client.get('/explore/accounts/')
        self.assertContains(page, '--card: #1d4ed8')
        self.assertContains(page, 'Add wallet')

    def test_transfer_needs_two_different_accounts(self):
        response = self.client.post('/transfer/', {'account': self.bank.pk, 'to_account': self.bank.pk, 'amount': '1', 'date': '2026-11-17'})
        self.assertContains(response, 'Pick two different accounts.')

    def test_rejects_zero_amount(self):
        response = self.add(amount='0')
        self.assertEqual(Transaction.objects.count(), 0)
        self.assertContains(response, 'Amount must be more than 0.')

    def test_activity_search(self):
        self.add(description='Grab')
        self.add(description='Netflix')
        response = self.client.get('/activity/?q=grab')
        self.assertContains(response, 'Grab')
        self.assertNotContains(response, 'Netflix')

    def test_edit_and_delete_transaction(self):
        self.add(description='Lunch')
        tx = Transaction.objects.get()
        self.client.post(f'/activity/{tx.pk}/edit/', {'kind': 'expense', 'amount': '150', 'description': 'Lunch',
                                                     'category': 'dining', 'account': self.bank.pk, 'date': '2026-11-17'})
        tx.refresh_from_db()
        self.assertEqual(tx.amount, 150)
        self.client.post(f'/activity/{tx.pk}/delete/')
        self.assertFalse(Transaction.objects.exists())

    def test_budget_tracks_this_months_spending(self):
        from django.utils import timezone
        budget = Budget.objects.create(user=self.user, category='dining', limit=1000)
        self.add(amount='250', category='dining', date=timezone.localdate().isoformat())
        response = self.client.get(f'/plan/budgets/{budget.pk}/')
        self.assertEqual(response.context['spent'], 250)
        self.assertEqual(response.context['left'], 750)
        self.assertContains(self.client.post('/plan/budgets/new/', {'category': 'dining', 'limit': '5'}), 'already have a budget')

    def test_goal_contributions_add_up(self):
        goal = Goal.objects.create(user=self.user, name='Emergency fund', target=1000)
        self.client.post(f'/plan/goals/{goal.pk}/add/', {'amount': '400', 'description': 'Monthly', 'date': '2026-11-01'})
        self.assertEqual(self.client.get(f'/plan/goals/{goal.pk}/').context['pct'], 40)

    def test_debt_payment_moves_plan_and_adds_expense(self):
        debt = Debt.objects.create(user=self.user, kind='installment', name='MacBook', total=1000, monthly=400, account=self.bank)
        for _ in range(4):  # last payment is capped at what's left
            self.client.post(f'/explore/debts/{debt.pk}/pay/')
        debt.refresh_from_db()
        self.assertEqual(debt.paid, 1000)
        self.assertEqual(sum(t.amount for t in Transaction.objects.all()), 1000)

    def test_credit_card_owed_and_payment(self):
        card = Account.objects.create(user=self.user, name='Visa', kind='credit', credit_limit=5000)
        self.add(amount='600', account=card.pk)
        self.assertEqual(self.client.get('/explore/cards/').context['cards'][0]['owed'], 600)
        self.client.post('/transfer/', {'account': self.bank.pk, 'to_account': card.pk, 'amount': '600', 'date': '2026-11-17'})
        self.assertEqual(self.client.get('/explore/cards/').context['cards'][0]['owed'], 0)

    def test_shared_household_equal_split(self):
        maya = make_user('maya@example.com', 'Maya')
        maya_bank = Account.objects.create(user=maya, name='BDO')
        self.client.post('/explore/shared/new/', {'name': 'Santos home', 'shared_budget': '20000'})
        self.client.post('/explore/shared/invite/', {'email': 'MAYA@example.com'})
        self.add(amount='700', shared='on')
        Transaction.objects.create(user=maya, account=maya_bank, amount=300, description='Rent', shared=True)
        people = {p['user'].first_name: p['balance'] for p in self.client.get('/explore/shared/').context['people']}
        self.assertEqual(people, {'Alex': 200, 'Maya': -200})

    def test_users_cannot_see_or_touch_each_others_data(self):
        self.add(description='Alex lunch')
        tx = Transaction.objects.get()
        other = make_user('maya@example.com', 'Maya')
        self.client.force_login(other)
        self.assertNotContains(self.client.get('/activity/'), 'Alex lunch')
        self.assertEqual(self.client.get(f'/activity/{tx.pk}/').status_code, 404)
        self.assertEqual(self.client.post(f'/activity/{tx.pk}/delete/').status_code, 404)
        self.assertEqual(self.client.get(f'/explore/accounts/{self.bank.pk}/edit/').status_code, 404)
        # can't log a transaction into someone else's account
        Account.objects.create(user=other, name='Mine')
        response = self.client.post('/add/', {'kind': 'expense', 'amount': '1', 'description': 'x', 'category': 'other',
                                              'account': self.bank.pk, 'date': '2026-11-17'})
        self.assertContains(response, 'Select a valid choice')

    def test_csv_export_only_has_my_rows(self):
        self.add(description='Mine')
        Transaction.objects.create(user=make_user('maya@example.com'), amount=5, description='Not mine')
        body = self.client.get('/explore/reports/export.csv').content.decode()
        self.assertIn('Mine', body)
        self.assertNotIn('Not mine', body)

    # ---- features from the screen recording ----

    def test_transfer_from_outside_and_to_outside_with_fee(self):
        self.client.post('/transfer/', {'source': 'external', 'destination': 'mine', 'to_account': self.gcash.pk,
                                        'amount': '500', 'date': '2026-11-17'})
        self.client.post('/transfer/', {'source': 'mine', 'destination': 'external', 'account': self.bank.pk,
                                        'amount': '200', 'fee': '15', 'date': '2026-11-17'})
        self.assertEqual(self.gcash.balance, 500)
        self.assertEqual(self.bank.balance, 1000 - 200 - 15)
        self.assertTrue(Transaction.objects.filter(kind='expense', category='fees', amount=15).exists())
        both_outside = self.client.post('/transfer/', {'source': 'external', 'destination': 'external', 'amount': '1', 'date': '2026-11-17'})
        self.assertContains(both_outside, 'At least one side must be one of your accounts.')

    def test_net_worth_assets_minus_liabilities(self):
        card = Account.objects.create(user=self.user, name='Visa', kind='credit')
        self.add(amount='300', account=card.pk)
        ctx = self.client.get('/explore/accounts/').context
        self.assertEqual((ctx['assets'], ctx['liabilities'], ctx['net']), (1000, 300, 700))

    def test_custom_category_is_saved_and_offered_again(self):
        self.add(new_category='Spotify', description='')
        tx = Transaction.objects.get()
        self.assertEqual((tx.category, tx.description), ('Spotify', 'Spotify'))
        self.assertContains(self.client.get('/add/'), 'value="Spotify"')

    def test_calculator_amount_still_validated_on_server(self):
        response = self.add(amount='12+3')  # JS works this out first; without JS the server refuses it
        self.assertEqual(Transaction.objects.count(), 0)
        self.assertContains(response, 'Enter a number')

    def test_recurring_and_someone_owes_me(self):
        self.add(amount='900', recurring='on', owed_by='Maya', owed_amount='300', description='Dinner')
        planned = self.user.planned.get()
        self.assertEqual((planned.amount, planned.repeat, str(planned.next_date)), (900, 'monthly', '2026-12-17'))
        owed = Debt.objects.get(kind='receivable')
        self.assertEqual((owed.name, owed.total), ('Maya', 300))
        self.client.post(f'/explore/debts/{owed.pk}/pay/')  # Maya pays back: shows up as income
        self.assertTrue(Transaction.objects.filter(kind='income', amount=300).exists())
        self.assertContains(self.add(owed_by='', owed_amount='50'), 'Who owes you?')

    def test_planned_payment_done_logs_it_and_moves_to_next_month(self):
        from datetime import date
        p = self.user.planned.create(name='Rent', amount=8000, account=self.bank, next_date=date(2027, 1, 31))
        self.client.post(f'/plan/planned/{p.pk}/done/')
        p.refresh_from_db()
        self.assertEqual(p.next_date, date(2027, 2, 28))  # month-end is clamped
        self.assertTrue(Transaction.objects.filter(description='Rent', amount=8000).exists())
        once = self.user.planned.create(name='Gift', amount=1, repeat='once')
        self.client.post(f'/plan/planned/{once.pk}/done/')
        once.refresh_from_db()
        self.assertFalse(once.active)

    def test_monthly_forecast_counts_planned_payments(self):
        from django.utils import timezone
        today = timezone.localdate()
        self.user.planned.create(name='Netflix', amount=549, next_date=today, repeat='monthly')
        self.user.planned.create(kind='income', name='Salary', amount=30000, next_date=today, repeat='weekly')
        first = self.client.get('/').context['forecast'][0]
        self.assertEqual(first['bills'], 549)
        self.assertEqual(first['income'] % 30000, 0)
        self.assertGreaterEqual(first['income'], 30000)

    def test_weekly_budget_only_counts_this_week(self):
        from datetime import timedelta
        from django.utils import timezone
        today = timezone.localdate()
        budget = Budget.objects.create(user=self.user, category='dining', limit=1000, period='weekly')
        start, end = budget.window(today)
        self.assertEqual((end - start).days, 7)
        self.assertTrue(start <= today < end)
        self.add(amount='100', category='dining', date=today.isoformat())
        self.add(amount='999', category='dining', date=(start - timedelta(days=1)).isoformat())
        self.assertEqual(self.client.get(f'/plan/budgets/{budget.pk}/').context['spent'], 100)

    def test_history_groups_by_day_with_totals(self):
        self.add(amount='100', date='2026-11-17')
        self.add(amount='50', kind='income', category='salary', date='2026-11-17')
        self.add(amount='30', date='2026-11-16')
        days = list(self.client.get('/activity/').context['days'])
        self.assertEqual([(str(d['date']), d['out'], d['in']) for d in days], [('2026-11-17', 100, 50), ('2026-11-16', 30, 0)])

    def test_tags_and_trips(self):
        from datetime import date
        self.add(amount='400', tags='Japan, food', date='2026-11-17')
        self.assertEqual(self.client.get('/plan/tags/').context['tags'][0]['tag'], 'japan')
        self.assertContains(self.client.get('/activity/?tag=japan'), '400.00')
        trip = self.user.trips.create(name='Japan', start=date(2026, 11, 16), end=date(2026, 11, 20), budget=1000)
        self.assertEqual(trip.spent, 400)

    def test_photo_is_private(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import override_settings
        import tempfile
        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            gif = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
            self.add(photo=SimpleUploadedFile('r.gif', gif, content_type='image/gif'))
            tx = Transaction.objects.get()
            response = self.client.get(f'/activity/{tx.pk}/photo/')
            self.assertEqual(response.status_code, 200)
            response.close()
            not_image = self.add(photo=SimpleUploadedFile('x.txt', b'hi', content_type='text/plain'))
            self.assertContains(not_image, 'Please choose an image.')
            self.client.force_login(make_user('maya@example.com'))
            self.assertEqual(self.client.get(f'/activity/{tx.pk}/photo/').status_code, 404)

    def test_every_page_loads(self):
        goal = Goal.objects.create(user=self.user, name='G', target=100)
        budget = Budget.objects.create(user=self.user, category='dining', limit=100)
        debt = Debt.objects.create(user=self.user, name='Loan', kind='loan', total=100, monthly=10)
        item = Investment.objects.create(user=self.user, name='Fund', invested=100, value=120)
        self.add(description='Lunch')
        tx = Transaction.objects.get()
        names = ['home', 'activity', 'add', 'transfer', 'plan', 'budgets', 'budget_new', 'goals', 'goal_new', 'cashflow',
                 'planned', 'planned_new', 'trips', 'trip_new', 'tags', 'receivables',
                 'accounts', 'account_new', 'cards', 'installments', 'loans', 'debt_new', 'investments',
                 'investment_new', 'reports', 'shared', 'household_new', 'settings', 'profile_edit', 'delete_account']
        urls = [reverse(n) for n in names] + [
            reverse('transaction', args=[tx.pk]), reverse('transaction_edit', args=[tx.pk]),
            reverse('budget', args=[budget.pk]), reverse('goal', args=[goal.pk]), reverse('goal_add', args=[goal.pk]),
            reverse('debt_edit', args=[debt.pk]), reverse('investment_edit', args=[item.pk]),
            '/explore/reports/?period=week', '/explore/reports/?period=year',
            '/?span=week', '/?span=month&forecast=5y', '/add/?scan=1', '/activity/?kind=income&tag=x&date=2026-11-17',
            '/explore/accounts/?show=liabilities&view=list',
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        Household.objects.create(name='H').members.add(self.user)
        self.assertEqual(self.client.get('/explore/shared/').status_code, 200)
