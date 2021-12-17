"""Tests of the club dashboard view"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_query

class ClubDashboardViewTestCase(TestCase):
    """Tests of the club dashboard view"""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.user = User.objects.get(username='johndoe')
        self.officer = User.objects.get(username='jonathandoe')

    def test_get_club_dashboard_view(self):
        self.client.login(username=self.user.username, password="Password123")

        url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_dashboard.html')

    def test_get_unexisting_club_dashboard_view(self):
        self.client.login(username=self.user.username, password="Password123")

        url = reverse('club_dashboard', kwargs={'club_id': 12345})
        response = self.client.get(url)
        redirect_url = reverse('user_dashboard')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_club_dashboard_view_redirects_not_logged_in(self):
        url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        redirect_url = reverse_with_query('log_in', query_kwargs={'next': url})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_club_dashboard_view_member(self):
        self.client.login(username=self.user.username, password="Password123")

        url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_dashboard.html')

    def test_pending_applications_hidden_to_non_officer(self):
        user2 = User.objects.get(username="janedoe")
        self.client.login(username=user2.username, password="Password123")
        url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_dashboard.html')
        self.assertNotContains(response, "<h2>Pending applications</h2>")

    def test_pending_applications_no_pending_application(self):
        self.client.login(username=self.officer.username, password="Password123")
        url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_dashboard.html')
        applications = list(response.context['applications'])
        self.assertEqual(len(applications), 0)
        self.assertContains(response, "<h2>Pending applications</h2>")
        self.assertContains(response, "<p>No pending applications</p>")

    def test_pending_applications_officer(self):
        self.client.login(username=self.officer.username, password="Password123")
        user2 = User.objects.get(username='janedoe')
        new_membership = Membership(user=user2, club=self.club, user_type="NM", application_status='P', personal_statement="Some personal statement")
        new_membership.save()
        url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_dashboard.html')
        applications = list(response.context['applications'])
        self.assertEqual(len(applications), 1)
        self.assertContains(response, "<h2>Pending applications</h2>")
        self.assertNotContains(response, "<p>No pending applications</p>")
        self.assertContains(response, "<td>Jane Doe</td>")
        self.assertContains(response, "<td>Some personal statement</td>")
