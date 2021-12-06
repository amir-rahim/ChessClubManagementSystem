"""Tests of the available_clubs view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club


class AvailableClubsViewTestCase(TestCase):
    """Tests of the available_clubs view."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_memberships.json',
        'clubs/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.user_non_member = User.objects.get(username="janedoe")
        self.url = reverse('available_clubs')

    def test_available_clubs_url(self):
        self.assertEqual(self.url, '/available_clubs/')

    def test_redirect_user_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_no_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'available_clubs.html')
        clubs = list(response.context['clubs'])
        self.assertEqual(len(clubs), 0)
        self.assertContains(response, "<p>There are no available clubs at the moment.</p>")

    def test_non_member_club(self):
        self.client.login(username=self.user_non_member.username, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'available_clubs.html')
        clubs = list(response.context['clubs'])
        self.assertIn(Club.objects.get(name="Royal Chess Club"), clubs)

    def test_multiple_clubs(self):
        new_user = User.objects.create_user(username='newuser', password='Password123', name="new user")
        new_user.save()

        self.client.login(username=new_user.username, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'available_clubs.html')
        clubs = list(response.context['clubs'])
        self.assertEqual(len(clubs), 2)
        self.assertEqual(clubs[0].name, "Kerbal Chess Club")
        self.assertEqual(clubs[1].name, "Royal Chess Club")
        self.assertNotContains(response, "<p>There are no available clubs at the moment.</p>")
