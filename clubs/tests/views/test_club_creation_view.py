"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from clubs.forms import ClubCreationForm
from clubs.models import User, Club, Membership
from clubs.tests.helpers import LogInTester, reverse_with_next

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
            'owner' : [self.user.pk],
            'location': "London, UK",
            'mission_statement': "My new club Statement",
            'description': "My new club description"
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
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_create_club(self):
        self.client.login(username="johndoe", password="Password123")
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('user_dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_cannot_create_club_named_with_already_taken_name(self):
        self.client.login(username="johndoe", password="Password123")
        self.form_input['name']="Royal Chess Club"
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('user_dashboard')
        self.assertEqual(response.status_code, 200)
