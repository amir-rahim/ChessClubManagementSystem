"""Unit tests for Elo Ratings."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, Club, Membership, Tournament, TournamentParticipation, Match, Group, EloRating
from django.utils.timezone import make_aware
from django.utils import timezone
import datetime

class EloRatingTestCase(TestCase):
    """Unit tests for Elo Ratings."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json'
    ]

    def setUp(self):
        self.owner = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name = "Kerbal Chess Club", owner=1)
        self.officer = User.objects.get(username='janedoe')
        self.officer_membership = Membership.objects.create(user = self.officer, club = self.club, personal_statement = "---")
        self.officer_membership.approve_membership()
        self.officer_membership.promote_to_officer()

        self.today = datetime.datetime.today()
        self.yesterday = self.today - datetime.timedelta(days=1)

        self.tournament = Tournament.objects.create(
            name = "Tournament 1",
            description = "Tournament description",
            club = self.club,
            date = make_aware(datetime.datetime(2021, 12, 25, 12, 0), timezone.utc),
            organizer = self.officer,
            capacity = 96,
            deadline = make_aware(datetime.datetime(2021, 12, 20, 12, 0), timezone.utc),
        )

    def test_tournament_add_16_participants(self):
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.SIGNUPS_OPEN)

        for i in range(16):
            User.objects.create(
                username = "user" + str(i),
                email = "user" + str(i) + "@example.com",
                password = "password"
            )
            Membership.objects.create(
                user = User.objects.get(username = "user" + str(i)),
                club = self.club,
                personal_statement = "---"
            )
            TournamentParticipation.objects.create(
                tournament = self.tournament,
                user = User.objects.get(username = "user" + str(i)),
            )


        self.tournament.deadline = make_aware(self.yesterday, timezone.utc)
        self.tournament.save()

        # Close Signups
        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.SIGNUPS_CLOSED)

        self.tournament.date = make_aware(self.yesterday, timezone.utc)
        self.tournament.save()

    def test_tournament_16_elimination_generate_matches_white_win(self):
        self.test_tournament_add_16_participants()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.ELIMINATION)

        self.tournament.generate_matches()
        for match in Match.objects.filter(tournament = self.tournament):
            white_player_membership = Membership.objects.get(user = match.white_player, club = self.club)
            black_player_membership = Membership.objects.get(user = match.black_player, club = self.club)

            white_elo_rating_before = EloRating.get_ratings(white_player_membership)[-1][0]
            black_elo_rating_before = EloRating.get_ratings(black_player_membership)[-1][0]

            match.result = Match.MatchResultTypes.WHITE_WIN
            match.save()

            white_elo_rating_after = EloRating.get_ratings(white_player_membership)[-1][0]
            black_elo_rating_after = EloRating.get_ratings(black_player_membership)[-1][0]

            self.assertTrue(white_elo_rating_after >= white_elo_rating_before)
            self.assertTrue(black_elo_rating_after <= black_elo_rating_before)

        self.tournament.check_tournament_stage_transition()

        for i in range(3):
            self.tournament.generate_matches()
            for match in Match.objects.filter(tournament = self.tournament):
                match.result = Match.MatchResultTypes.WHITE_WIN
                match.save()

            self.tournament.check_tournament_stage_transition()


        self.assertEqual(self.tournament.stage, Tournament.StageTypes.FINISHED)
