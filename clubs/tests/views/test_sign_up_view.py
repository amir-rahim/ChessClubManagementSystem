"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from clubs.forms import SignUpForm
from clubs.models import User
from clubs.tests.helpers import LogInTester

class SignUpViewTestCase(TestCase, LogInTester):
    """Tests of the sign up view."""

    fixtures = [
            'clubs/tests/fixtures/default_users.json'
    ]

    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'name': 'Janet Doe',
            'username': 'janetdoe',
            'email': 'janetdoe@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }
        self.user = User.objects.get(username='johndoe')

    def test_sign_up_url(self):
        self.assertEqual(self.url,'/sign_up/')

    def test_get_sign_up(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')

        form = response.context['form']

        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_get_sign_up_redirects_when_logged_in(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('user_dashboard')

        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_dashboard.html')

    def test_unsuccesful_sign_up(self):
        self.form_input['username'] = 'BAD_USERNAME'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()

        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')

        form = response.context['form']

        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_succesful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()

        self.assertEqual(after_count, before_count+1)

        response_url = reverse('user_dashboard')

        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_dashboard.html')

        user = User.objects.get(username='janetdoe')

        self.assertEqual(user.name, 'Janet Doe')
        self.assertEqual(user.email, 'janetdoe@example.org')

        is_password_correct = check_password('Password123', user.password)

        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())

    def test_post_sign_up_redirects_when_logged_in(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()

        self.assertEqual(after_count, before_count)

        redirect_url = reverse('user_dashboard')

        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_dashboard.html')
