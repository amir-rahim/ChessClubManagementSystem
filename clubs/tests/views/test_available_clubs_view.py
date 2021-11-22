"""Tests of the available_clubs view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club


class AvailableClubsViewTestCase(TestCase):
    """Tests of the available_clubs view."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.user2 = User.objects.get(username="janedoe")
        self.url = reverse('available_clubs')

    def test_user_dashboard_url(self):
        self.assertEqual(self.url,'/available_clubs/')

    # def test_redirect_user_not_logged_in(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 302)

    def test_no_club(self):
        self.client.login(username=self.user.username, password='Password123')
        #Create 0 club
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'available_clubs.html')
        list_of_clubs = list(response.context['list_of_clubs'])
        self.assertEqual(len(list_of_clubs), 0)

    def test_single_club(self):
        self.client.login(username=self.user.username, password='Password123')
        #Create 1 club
        new_club = Club.objects.create(name="New club 1", owner=self.user)
        new_club.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'available_clubs.html')
        list_of_clubs = list(response.context['list_of_clubs'])
        self.assertEqual(len(list_of_clubs), 1)
        self.assertEqual(list_of_clubs[0]["name"], "New club 1")
        self.assertEqual(list_of_clubs[0]["owner"], self.user.name)

    def test_multiple_clubs(self):
        self.client.login(username=self.user.username, password='Password123')
        #Create 2 clubs
        new_club = Club.objects.create(name="New club 1", owner=self.user)
        new_club.save()
        new_club = Club.objects.create(name="New club 2", owner=self.user2)
        new_club.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'available_clubs.html')
        list_of_clubs = list(response.context['list_of_clubs'])
        self.assertEqual(len(list_of_clubs), 2)
        self.assertEqual(list_of_clubs[0]["name"], "New club 1")
        self.assertEqual(list_of_clubs[0]["owner"], self.user.name)
        self.assertEqual(list_of_clubs[1]["name"], "New club 2")
        self.assertEqual(list_of_clubs[1]["owner"], self.user2.name)
