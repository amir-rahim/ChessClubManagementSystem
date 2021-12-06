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
    # #
    # # def test_owner_cannot_apply_own_club(self):
    # #     self.client.login(username="johndoe", password="Password123")
    # #     response = self.client.get(self.url)
    # #     form = response.context['form']
    # #     form.cleaned_data = self.form_input
    # #     form.data = self.form_input
    # #     ##form.save()
    # #     self.assertFalse(form.is_valid())
    #
    # def test_owner_cannot_apply_own_club(self):
    #     self.client.login(username="johndoe", password="Password123")
    #     response = self.client.get(self.url)
    #     form = response.context['form']
    #     form.cleaned_data = self.form_input
    #     #form.save()
    #     self.assertFalse(form.is_valid())
    #
    # # def test_form_shows_all_clubs(self):
    # #     self.client.login(username="johndoe", password="Password123")
    # #     response = self.client.get(self.url)
    # #     form = response.context['form']
    # #     self.assertEqual(len(form['club'].field.queryset), Club.objects.count())
    #
    #
    # # def test_cannot_apply_twice(self):
    # #     self.client.login(username="janedoe", password="Password123")
    # #     response = self.client.get(self.url)
    # #     form = response.context['form']
    # #     form.cleaned_data = self.form_input
    # #     before_count = Membership.objects.count()
    # #     form.save()
    # #     after_count = Membership.objects.count()
    # #     self.assertEqual(after_count, before_count + 1)
    #
    #     #response = self.client.get(self.url)
    #     #form = response.context['form']
    #     #form.cleaned_data = self.form_input
    #     #form.save()
    #     #self.assertFalse(form.is_valid())
