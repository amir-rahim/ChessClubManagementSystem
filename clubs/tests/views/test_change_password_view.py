"""Tests for the change password view."""
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from clubs.forms import ChangePasswordForm
from clubs.models import User
from clubs.tests.helpers import reverse_with_query

class PasswordViewTest(TestCase):
    """Test suite for the change password view."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.url = reverse('change_password')
        self.form_input = {
            'current_password': 'Password123',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123',
        }

    def test_change_password_url(self):
        self.assertEqual(self.url, '/user_profile/change_password')

    def test_get_change_password(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change_password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ChangePasswordForm))

    def test_get_change_password_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_query('log_in', query_kwargs={'next': self.url})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_password_change(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('user_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_profile.html')
        self.user.refresh_from_db()
        is_password_correct = check_password('NewPassword123', self.user.password)
        self.assertTrue(is_password_correct)

    def test_password_change_unsuccessful_without_correct_old_password(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['current_password'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change_password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ChangePasswordForm))
        self.user.refresh_from_db()
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)

    def test_password_change_unsuccessful_without_password_confirmation(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['password_confirmation'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change_password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ChangePasswordForm))
        self.user.refresh_from_db()
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_query('log_in', query_kwargs={'next': self.url})
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)
