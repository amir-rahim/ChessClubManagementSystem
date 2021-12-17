"""Tests of the generate_matches functionalities"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Tournament, TournamentParticipation
from clubs.tests.helpers import reverse_with_query
from django.contrib.messages import get_messages
from django.utils.timezone import make_aware
from django.utils import timezone
from datetime import datetime

class CancelTournamentTestCase(TestCase):
    """Tests of the cancel_tournament functionalities"""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json',
        'clubs/tests/fixtures/default_tournaments.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.officer = User.objects.get(username="johndoe")
        self.user = User.objects.get(username="alicesmith")
        self.non_member = User.objects.get(username="juliedoe")
        self.tournament = Tournament.objects.get(name="Tournament 1")
 
        self.tournament.date = make_aware(datetime(2099, 1, 1, 0, 0, 0))
        self.tournament.deadline = make_aware(datetime(2020, 1, 1, 0, 0, 0))
        self.tournament.save()
        
        self.tournament.check_tournament_stage_transition()

    def test_cancel_tournament(self):
        self.tournament.organizer = self.officer
        self.tournament.save()

        self.client.login(username=self.officer.username, password="Password123")
        url = reverse('cancel_tournament', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        with self.assertRaises(Tournament.DoesNotExist):
            Tournament.objects.get(id=self.tournament.id)

    def test_generate_matches_tournament_with_next(self):
        self.tournament.organizer = self.officer
        self.tournament.save()

        self.client.login(username=self.officer.username, password="Password123")
        next_url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        url = reverse_with_query('cancel_tournament', {'tournament_id': self.tournament.id}, {'next': next_url})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, next_url)

        with self.assertRaises(Tournament.DoesNotExist):
            Tournament.objects.get(id=self.tournament.id)

    def test_invalid_generate_matches_tournament(self):
        self.client.login(username=self.non_member.username, password="Password123")
        url = reverse('cancel_tournament', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0)
        for message in messages:
            self.assertEqual(message.tags, "danger")


