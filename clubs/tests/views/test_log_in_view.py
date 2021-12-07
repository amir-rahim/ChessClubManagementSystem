"""Tests of the log in view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.forms import LogInForm
from clubs.models import User
from clubs.tests.helpers import LogInTester, reverse_with_query

class LogInViewTestCase(TestCase, LogInTester):
    """Tests of the log in view."""

    fixtures = ["clubs/tests/fixtures/default_users.json"]

    def setUp(self):
        self.url = reverse('log_in')
        self.user = User.objects.get(username="johndoe")

    def test_log_in_url(self):
        self.assertEqual(self.url,'/log_in/')

    def test_get_log_in(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')

        form = response.context['form']
        next = response.context['next']

        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(next)

        messages_list = list(response.context['messages'])

        self.assertEqual(len(messages_list), 0)

    def test_get_log_in_with_redirect(self):
        destination_url = reverse('user_dashboard')
        self.url = reverse_with_query('log_in', query_kwargs={'next': destination_url})
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')

        form = response.context['form']
        next = response.context['next']

        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertEqual(next, destination_url)

        messages_list = list(response.context['messages'])

        self.assertEqual(len(messages_list), 0)

    def test_unsuccesful_log_in(self):
        form_input = { 'username': '@johndoe', 'password': 'WrongPassword123' }
        response = self.client.post(self.url, form_input)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')

        form = response.context['form']

        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())

        messages_list = list(response.context['messages'])

        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_username(self):
        form_input = { 'username': '', 'password': 'Password123' }
        response = self.client.post(self.url, form_input)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')

        form = response.context['form']

        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())

        messages_list = list(response.context['messages'])

        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_password(self):
        form_input = { 'username': '@johndoe', 'password': '' }
        response = self.client.post(self.url, form_input)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')

        form = response.context['form']

        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())

        messages_list = list(response.context['messages'])

        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_succesful_log_in_with_redirect(self):
        redirect_url = reverse('user_dashboard')
        form_input = { 'username': 'johndoe', 'password': 'Password123', 'next': redirect_url }
        response = self.client.post(self.url, form_input, follow=True)

        self.assertTrue(self._is_logged_in())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_dashboard.html')

        messages_list = list(response.context['messages'])

        self.assertEqual(len(messages_list), 0)

    def test_succesful_log_in(self):
        form_input = { 'username': 'johndoe', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)

        self.assertTrue(self._is_logged_in())

        response_url = reverse('user_dashboard')

        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_dashboard.html')

        messages_list = list(response.context['messages'])

        self.assertEqual(len(messages_list), 0)

    def test_valid_log_in_by_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        form_input = { 'username': 'johndoe', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')

        form = response.context['form']

        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())

        messages_list = list(response.context['messages'])

        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
