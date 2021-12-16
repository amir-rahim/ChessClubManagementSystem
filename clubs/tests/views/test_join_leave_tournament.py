"""Tests of the accept_membership and reject_membership functionalities"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Tournament, TournamentParticipation
from clubs.tests.helpers import reverse_with_query

class JoinLeaveTournamentTestCase(TestCase):
    """Tests of the join_tournament and leave_tournament functionalities"""

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

    def test_join_tournament(self):
        self.client.login(username=self.user.username, password="Password123")
        url = reverse('join_tournament', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(TournamentParticipation.objects.filter(user=self.user, tournament=self.tournament).exists())

    def test_join_tournament_with_next(self):
        self.client.login(username=self.user.username, password="Password123")
        next_url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        url = reverse_with_query('join_tournament', {'tournament_id': self.tournament.id}, {'next': next_url})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TournamentParticipation.objects.filter(user=self.user, tournament=self.tournament).exists())

    def test_invalid_join_tournament(self):
        self.client.login(username=self.non_member.username, password="Password123")
        url = reverse('join_tournament', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TournamentParticipation.objects.filter(user=self.user, tournament=self.tournament).exists())

    def test_leave_tournament(self):
        self.client.login(username=self.user.username, password="Password123")
        TournamentParticipation.objects.create(user=self.user, tournament=self.tournament)
        self.assertTrue(TournamentParticipation.objects.filter(user=self.user, tournament=self.tournament).exists())
        url = reverse('leave_tournament', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TournamentParticipation.objects.filter(user=self.user, tournament=self.tournament).exists())

    def test_leave_tournament_with_next(self):
        self.client.login(username=self.user.username, password="Password123")
        TournamentParticipation.objects.create(user=self.user, tournament=self.tournament)
        self.assertTrue(TournamentParticipation.objects.filter(user=self.user, tournament=self.tournament).exists())
        next_url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        url = reverse_with_query('leave_tournament', {'tournament_id': self.tournament.id}, {'next': next_url})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TournamentParticipation.objects.filter(user=self.user, tournament=self.tournament).exists())

    def test_invalid_leave_tournament(self):
        self.client.login(username=self.non_member.username, password="Password123")
        self.assertFalse(TournamentParticipation.objects.filter(user=self.user, tournament=self.tournament).exists())
        url = reverse('leave_tournament', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TournamentParticipation.objects.filter(user=self.user, tournament=self.tournament).exists())
