import re

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

NEW = 'fresh-squirrel-42'


class ForgotPasswordTests(TestCase):
    def setUp(self):
        self.alex = User.objects.create_user('alex@example.com', 'alex@example.com', 'old-squirrel-26', first_name='Alex')

    def reset_link(self):
        return re.search(r'https?://[^/]+(/password/reset/\S+/)', mail.outbox[-1].body).group(1)

    def test_login_page_links_to_forgot_password(self):
        self.assertContains(self.client.get('/login/'), '/password/forgot/')

    def test_full_reset_flow(self):
        response = self.client.post('/password/forgot/', {'email': 'ALEX@example.com'})
        self.assertRedirects(response, '/password/forgot/sent/')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Hi Alex', mail.outbox[0].body)

        form_page = self.client.get(self.reset_link(), follow=True)  # Django swaps the token for a session step
        self.assertContains(form_page, 'Choose a new password.')
        done = self.client.post(form_page.redirect_chain[-1][0], {'new_password1': NEW, 'new_password2': NEW})
        self.assertRedirects(done, '/password/reset/done/')

        self.assertRedirects(self.client.post('/login/', {'username': 'alex@example.com', 'password': NEW}), '/')
        self.client.post('/logout/')
        old = self.client.post('/login/', {'username': 'alex@example.com', 'password': 'old-squirrel-26'})
        self.assertContains(old, 'Email/username or password is incorrect.')

    def test_link_works_only_once(self):
        self.client.post('/password/forgot/', {'email': 'alex@example.com'})
        link = self.reset_link()
        page = self.client.get(link, follow=True)
        self.client.post(page.redirect_chain[-1][0], {'new_password1': NEW, 'new_password2': NEW})
        self.assertContains(self.client.get(link, follow=True), "This link doesn't work anymore.")

    def test_unknown_email_looks_the_same_but_sends_nothing(self):
        response = self.client.post('/password/forgot/', {'email': 'nobody@example.com'})
        self.assertRedirects(response, '/password/forgot/sent/')  # doesn't reveal who has an account
        self.assertEqual(mail.outbox, [])

    def test_superuser_with_username_can_reset_by_email(self):
        User.objects.create_superuser('capstoneadmin', 'boss@example.com', 'old-squirrel-26')
        self.client.post('/password/forgot/', {'email': 'boss@example.com'})
        page = self.client.get(self.reset_link(), follow=True)
        self.client.post(page.redirect_chain[-1][0], {'new_password1': NEW, 'new_password2': NEW})
        self.assertRedirects(self.client.post('/login/', {'username': 'capstoneadmin', 'password': NEW}), '/')

    def test_weak_or_mismatched_new_password_is_refused(self):
        self.client.post('/password/forgot/', {'email': 'alex@example.com'})
        page = self.client.get(self.reset_link(), follow=True)
        url = page.redirect_chain[-1][0]
        self.assertContains(self.client.post(url, {'new_password1': NEW, 'new_password2': 'different-42'}), 'didn')
        self.assertContains(self.client.post(url, {'new_password1': '123', 'new_password2': '123'}), 'too short')
