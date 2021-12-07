"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership, Tournament
from clubs.forms import TournamentCreationForm
from clubs.tests.helpers import LogInTester, reverse_with_query
from django.utils.timezone import make_aware
from django.utils import timezone
import datetime

class TournamentCreationViewTestCase(TestCase, LogInTester):
    """Tests of the tournament creation view."""

    fixtures = [
            'clubs/tests/fixtures/default_users.json',
            'clubs/tests/fixtures/default_clubs.json',
            'clubs/tests/fixtures/default_memberships.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(name = "Kerbal Chess Club", owner=1)
        self.officer = User.objects.get(username='janedoe')
        self.officer_membership = Membership.objects.create(user = self.officer, club = self.club, personal_statement = "---")
        self.officer_membership.approve_membership()
        self.officer_membership.promote_to_officer()
        self.form_input = {
            'name': "Tournament 1",
            'description': "Tournament description",
            'organizer': self.officer.id,
            'club': self.club.pk,
            'date': make_aware(datetime.datetime(2021, 12, 25, 12, 0), timezone.utc),
            'capacity': 2,
            'deadline': make_aware(datetime.datetime(2021, 12, 20, 12, 0), timezone.utc),
        }
        self.url = reverse('new_tournament', kwargs={'club_id': self.club.id})

    def test_tournament_creation_url(self):
        self.assertEqual(self.url,  f'/new_tournament/{self.club.id}')

    def test_get_tournament_creation(self):
        self.client.login(username="janedoe", password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_tournament.html')

        form = response.context['form']

        self.assertTrue(isinstance(form, TournamentCreationForm))
        self.assertFalse(form.is_bound)

    def test_get_tournament_creation_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_query('log_in', query_kwargs={'next': self.url})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_create_tournament(self):
        self.client.login(username="janedoe", password="Password123")
        before_count = Tournament.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('user_dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_not_valid_tournament(self):
        self.form_input['capacity'] = 1
        self.client.login(username="janedoe", password="Password123")
        before_count = Tournament.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)

    def test_member_cannot_create_torunament(self):
        self.form_input['organizer'] = User.objects.get(username="johndoe")
        self.client.login(username="janedoe", password="Password123")
        before_count = Tournament.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('user_dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
