"""Tests of the club dashboard view"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club
from clubs.tests.helpers import reverse_with_next

class ClubDashboardViewTestCase(TestCase):
    """Tests of the home view"""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.user = User.objects.get(username='johndoe')
        self.officer = User.objects.get(username='jonhatandoe')

    def test_get_club_dashboard_view(self):
        self.client.login(username=self.user.username, password="Password123")

        url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_dashboard.html')

    def test_club_dashboard_view_redirects_not_logged_in(self):
        url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        redirect_url = reverse_with_next('log_in', url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
 
    def test_club_dashboard_view_member(self):
        self.client.login(username=self.user.username, password="Password123")

        url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_dashboard.html')


