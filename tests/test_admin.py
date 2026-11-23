from django.contrib.auth.models import User
from django.test import TestCase

from apps.transactions.models import Transaction
from apps.wallets.models import Account

ADMIN_PAGES = ['/settings/admin/', '/settings/admin/users/', '/backup/download/']


class AdminDashboardTests(TestCase):
    def setUp(self):
        self.boss = User.objects.create_superuser('boss@example.com', 'boss@example.com', 'pw', first_name='Boss')
        self.alex = User.objects.create_user('alex@example.com', 'alex@example.com', 'pw', first_name='Alex')
        bank = Account.objects.create(user=self.alex, name='BPI')
        Transaction.objects.create(user=self.alex, account=bank, amount=150, description='Lunch')

    def test_normal_users_and_visitors_cannot_see_admin_pages(self):
        for url in ADMIN_PAGES + [f'/settings/admin/users/{self.alex.pk}/']:
            with self.subTest(url=url, who='visitor'):
                self.assertNotEqual(self.client.get(url).status_code, 200)
        self.client.force_login(self.alex)
        for url in ADMIN_PAGES + [f'/settings/admin/users/{self.boss.pk}/']:
            with self.subTest(url=url, who='normal user'):
                self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(f'/settings/admin/users/{self.boss.pk}/delete/').status_code, 404)
        self.assertTrue(User.objects.filter(pk=self.boss.pk).exists())
        self.assertNotContains(self.client.get('/settings/'), 'Admin panel')

    def test_superuser_sees_dashboard_users_and_records(self):
        self.client.force_login(self.boss)
        self.assertContains(self.client.get('/settings/'), 'Admin panel')
        dash = self.client.get('/settings/admin/')
        self.assertEqual((dash.context['users'], dash.context['transactions']), (2, 1))
        self.assertContains(self.client.get('/settings/admin/users/?q=alex'), 'alex@example.com')
        self.assertNotContains(self.client.get('/settings/admin/users/?q=alex'), 'boss@example.com')
        self.assertContains(self.client.get('/settings/admin/users/?show=superusers'), 'boss@example.com')
        detail = self.client.get(f'/settings/admin/users/{self.alex.pk}/')
        self.assertContains(detail, 'Lunch')
        backup = self.client.get('/backup/download/')
        self.assertEqual(backup['Content-Type'], 'application/json')

    def test_deactivate_and_delete_another_user(self):
        self.client.force_login(self.boss)
        self.client.post(f'/settings/admin/users/{self.alex.pk}/toggle/')
        self.alex.refresh_from_db()
        self.assertFalse(self.alex.is_active)
        self.assertContains(self.client.get('/settings/admin/users/?show=inactive'), 'alex@example.com')
        self.client.post(f'/settings/admin/users/{self.alex.pk}/delete/')
        self.assertFalse(User.objects.filter(pk=self.alex.pk).exists())
        self.assertFalse(Transaction.objects.exists())  # their records go with them

    def test_superuser_cannot_lock_themselves_out(self):
        self.client.force_login(self.boss)
        self.client.post(f'/settings/admin/users/{self.boss.pk}/toggle/')
        self.client.post(f'/settings/admin/users/{self.boss.pk}/delete/')
        self.boss.refresh_from_db()
        self.assertTrue(self.boss.is_active)

    def test_actions_need_post(self):
        self.client.force_login(self.boss)
        self.assertEqual(self.client.get(f'/settings/admin/users/{self.alex.pk}/delete/').status_code, 405)
        self.assertTrue(User.objects.filter(pk=self.alex.pk).exists())
