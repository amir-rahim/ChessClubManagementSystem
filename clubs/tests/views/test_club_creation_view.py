"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from clubs.forms import ClubCreationForm
from clubs.models import User, Club, Membership
from clubs.tests.helpers import LogInTester, reverse_with_query

class ClubCreationViewTestCase(TestCase, LogInTester):
    """Tests of the club creation view."""

    fixtures = [
            'clubs/tests/fixtures/default_users.json',
            'clubs/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.url = reverse('new_club')
        self.user = User.objects.get(username='johndoe')
        self.form_input = {
            'name' : "My new club",
            'owner' : self.user
        }

    def test_club_creation_url(self):
        self.assertEqual(self.url,'/new_club/')

    def test_get_club_creation(self):
        self.client.login(username="johndoe", password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_club.html')

        form = response.context['form']

        self.assertTrue(isinstance(form, ClubCreationForm))
        self.assertFalse(form.is_bound)

    def test_club_creation_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_query('log_in', query_kwargs={'next': self.url})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
