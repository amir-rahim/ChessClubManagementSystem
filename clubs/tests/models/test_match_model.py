"""Unit tests for the Match model."""
from django.test import TestCase
from django.core.exceptions import ValidationError
from clubs.models import User, Club, Tournament, Match
from django.utils.timezone import make_aware
from django.utils import timezone
import datetime

class MatchModelTestCase(TestCase):
    """Unit tests for the TournamentParticipation model."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_tournaments.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(name = "Kerbal Chess Club", owner=1)
        self.officer = User.objects.get(username='janedoe')
        self.tournament = Tournament.objects.get(name="Tournament 1")
        self.white_player = User.objects.get(username="alicesmith")
        self.black_player = User.objects.get(username="bobsmith")


    def test_match_object_creation(self):
        before = Match.objects.count()
        Match.objects.create(
            white_player = self.white_player,
            black_player = self.black_player,
            tournament = self.tournament
        )
        after = Match.objects.count()
        self.assertEqual(before+1, after)

    def test_match_set_null(self):
        before = Match.objects.count()
        match = Match.objects.create(
            white_player = self.white_player,
            black_player = self.black_player,
            tournament = self.tournament
        )
        after = Match.objects.count()
        self.assertEqual(before+1, after)
        
        self.white_player.delete()
        
        match.refresh_from_db()
        self.assertEqual(match.white_player, None)

    def test_match_award_pending(self):
        before = Match.objects.count()
        match = Match.objects.create(
            white_player = self.white_player,
            black_player = self.black_player,
            tournament = self.tournament
        )
        after = Match.objects.count()
        self.assertEqual(before+1, after)
        self.assertEqual(match.result, Match.MatchResultTypes.PENDING)

        self.assertEqual(match.get_match_award_for_user(self.white_player), 0)
        self.assertEqual(match.get_match_award_for_user(self.black_player), 0)


    def test_match_award_win(self):
        before = Match.objects.count()
        match = Match.objects.create(
            white_player = self.white_player,
            black_player = self.black_player,
            tournament = self.tournament
        )
        after = Match.objects.count()
        self.assertEqual(before+1, after)
        self.assertEqual(match.result, Match.MatchResultTypes.PENDING)

        match.result = Match.MatchResultTypes.WHITE_WIN
        match.save()

        self.assertEqual(match.get_match_award_for_user(self.white_player), 1)
        self.assertEqual(match.get_match_award_for_user(self.black_player), 0)

        match.result = Match.MatchResultTypes.BLACK_WIN
        match.save()

        self.assertEqual(match.get_match_award_for_user(self.white_player), 0)
        self.assertEqual(match.get_match_award_for_user(self.black_player), 1)


    def test_match_award_draw(self):
        before = Match.objects.count()
        match = Match.objects.create(
            white_player = self.white_player,
            black_player = self.black_player,
            tournament = self.tournament
        )
        after = Match.objects.count()
        self.assertEqual(before+1, after)
        self.assertEqual(match.result, Match.MatchResultTypes.PENDING)

        match.result = Match.MatchResultTypes.DRAW
        match.save()

        self.assertEqual(match.get_match_award_for_user(self.white_player), 0.5)
        self.assertEqual(match.get_match_award_for_user(self.black_player), 0.5)

    def test_match_award_user_not_in_match(self):
        match = Match.objects.create(
            white_player = self.white_player,
            black_player = self.black_player,
            tournament = self.tournament,
            result = Match.MatchResultTypes.WHITE_WIN
        )
        match.save()

        self.assertRaises(ValueError, match.get_match_award_for_user, self.officer) 

