"""Unit tests for the Tournament model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, Club, Membership, Tournament, TournamentParticipation, Match, Group
from django.utils.timezone import make_aware
from django.utils import timezone
import datetime

import operator as op
from functools import reduce

def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    return numer // denom

class TournamentModelTestCase(TestCase):
    """Unit tests for the Tournament model."""

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

    def test_is_officer(self):
        self.assertEqual(self.officer_membership.user_type, "OF")

    def test_create_tournament(self):
        before = Tournament.objects.count()
        Tournament.objects.create(
            name = "Tournament 1",
            description = "Tournament description",
            club = self.club,
            date = make_aware(datetime.datetime(2021, 12, 25, 12, 0), timezone.utc),
            organizer = self.officer,
            capacity = 2,
            deadline = make_aware(datetime.datetime(2021, 12, 20, 12, 0), timezone.utc),
        )
        after = Tournament.objects.count()
        self.assertEqual(after, before+1)

    def test_cannot_create_tournaments_with_same_name(self):
        before = Tournament.objects.count()
        with self.assertRaises(Exception) as context:
            Tournament.objects.create(
                name = "Tournament 1",
                description = "Tournament description",
                club = self.club,
                date = make_aware(datetime.datetime(2021, 12, 25, 12, 0), timezone.utc),
                organizer = self.officer,
                capacity = 2,
                deadline = make_aware(datetime.datetime(2021, 12, 20, 12, 0), timezone.utc),
            )
            after = Tournament.objects.count()
            Tournament.objects.create(
                name = "Tournament 1",
                description = "Tournament description",
                club = self.club,
                date = make_aware(datetime.datetime(2021, 12, 25, 12, 0), timezone.utc),
                organizer = self.officer,
                capacity = 2,
                deadline = make_aware(datetime.datetime(2021, 12, 20, 12, 0), timezone.utc),
            )
            after = Tournament.objects.count()

        self.assertEqual(after, before+1)


class TournamentModelMatchesTestCase(TestCase):
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


    def test_tournament_add_96_participants(self):
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.SIGNUPS_OPEN)

        for i in range(0, self.tournament.capacity):
            User.objects.create(
                username = "user" + str(i),
                email = "user" + str(i) + "@example.com",
                password = "password"
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

    def test_tournament_96_group_stages_phase_0_generate_matches(self):
        self.test_tournament_add_96_participants()
        
        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.GROUP_STAGES)

        self.tournament.generate_matches()

        participants = self.tournament.competing_players()
        group_count = len(participants) // self.tournament.group_size
        match_count = Match.objects.filter(tournament = self.tournament).count()

        self.assertEqual(self.tournament.group_phase, 0)
        self.assertEqual(match_count, group_count * ncr(self.tournament.group_size, 2))

    def test_tournament_96_group_stages_phase_0_white_win(self):
        self.test_tournament_96_group_stages_phase_0_generate_matches()

        for match in Match.objects.filter(tournament = self.tournament):
            match.result = Match.MatchResultTypes.WHITE_WIN
            match.save()

        self.tournament.check_tournament_stage_transition()
        
        participants = self.tournament.competing_players()

        # TODO: Add assertion

        #self.assertEqual(len(participants), len(participants) // self.tournament.group_size )


    def test_tournament_96_group_stages_phase_1_generate_matches(self):
        self.test_tournament_96_group_stages_phase_0_white_win()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.GROUP_STAGES)

        self.tournament.generate_matches()

        participants = self.tournament.competing_players()
        group_count = len(participants) // self.tournament.group_size

        phase_1_groups = Group.objects.filter(tournament=self.tournament, phase=1)
        match_count = 0
        for group in phase_1_groups:
            match_count += Match.objects.filter(tournament = self.tournament, group = group).count()

        self.assertEqual(self.tournament.group_phase, 1)
        self.assertEqual(match_count, group_count * ncr(self.tournament.group_size, 2))

    def test_tournament_96_group_stages_phase_1_white_win(self):
        self.test_tournament_96_group_stages_phase_1_generate_matches()

        for match in Match.objects.filter(tournament = self.tournament):
            match.result = Match.MatchResultTypes.WHITE_WIN
            match.save()

        self.tournament.check_tournament_stage_transition()
        
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.ELIMINATION)

    def test_tournament_96_elimination_generate_matches_white_win(self):
        self.test_tournament_96_group_stages_phase_1_white_win()

        
        while self.tournament.stage == Tournament.StageTypes.ELIMINATION:
            self.tournament.generate_matches()

            for match in Match.objects.filter(tournament = self.tournament):
                match.result = Match.MatchResultTypes.WHITE_WIN
                match.save()

            self.tournament.check_tournament_stage_transition()

        
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.FINISHED)
