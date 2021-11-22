"""Tests of the available_clubs view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club


class ClubMembershipsViewTestCase(TestCase):
    """Tests of the available_clubs view."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.user2 = User.objects.get(username="janedoe")

        self.club = Club.objects.get(name = "Kerbal Chess Club") # Owner: johndoe, Membership: johndoe
        self.club2 = Club.objects.get(name = "Royal Chess Club") # Owner: janedoe, Membership: johndoe, janedoe

        self.url = reverse('club_memberships')

    def test_user_dashboard_url(self):
        self.assertEqual(self.url,'/club_memberships/')

    def test_redirect_user_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_no_clubs(self):
        new_user = User.objects.create_user(username='newuser', password='Password123', name="new user")
        new_user.save()

        self.client.login(username=new_user.username, password='Password123')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_memberships.html')
        clubs = list(response.context['clubs'])
        self.assertEqual(len(clubs), 0)

    def test_clubs(self):
        self.client.login(username=self.user.username, password='Password123')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_memberships.html')
        clubs = list(response.context['clubs'])
        self.assertEqual(len(clubs), 2)
        self.assertEqual(clubs[0].name, self.club.name)
        self.assertEqual(clubs[1].name, self.club2.name)

     
