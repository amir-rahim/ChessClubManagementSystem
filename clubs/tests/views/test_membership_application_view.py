"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from clubs.forms import MembershipApplicationForm
from clubs.models import User, Club
from clubs.tests.helpers import LogInTester, reverse_with_next

class MembershipApplicationViewTestCase(TestCase, LogInTester):
    """Tests of the membership application view."""

    fixtures = [
            'clubs/tests/fixtures/default_users.json',
            'clubs/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.url = reverse('membership_application')
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='Kerbal Chess Club')
        self.form_input = {
            'club' : self.club,
            'user' : self.user
        }

    def test_membership_application_url(self):
        self.assertEqual(self.url,'/membership_application/')

    def test_get_membership_application(self):
        self.client.login(username="johndoe", password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'apply.html')

        form = response.context['form']

        self.assertTrue(isinstance(form, MembershipApplicationForm))
        self.assertFalse(form.is_bound)

    def test_get_membership_application_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
