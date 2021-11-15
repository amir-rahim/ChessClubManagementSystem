"""Tests of the user dashboard view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from clubs.tests.helpers import reverse_with_next


class UserDashboardViewTestCase(TestCase):
    """Tests of the user dashboard view."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.url = reverse('user_dashboard')

    def test_user_dashboard_url(self):
        self.assertEqual(self.url,'/user_dashboard/')

    def test_get_user_dashboard(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_dashboard.html')

    def test_get_user_dashboard_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)