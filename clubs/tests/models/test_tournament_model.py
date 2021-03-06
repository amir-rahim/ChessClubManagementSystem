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
        self.officer = User.objects.get(username='jonathandoe')
        self.officer_membership = Membership.objects.get(user = self.officer, club = self.club)
        self.member = User.objects.get(username='janettedoe')
        self.tournament = Tournament.objects.create(
            name = "Tournament 1",
            description = "Tournament description",
            club = self.club,
            date = make_aware(datetime.datetime(2022, 12, 25, 12, 0), timezone.utc),
            organizer = self.officer,
            capacity = 2,
            deadline = make_aware(datetime.datetime(2022, 12, 20, 12, 0), timezone.utc),
        )
        self.tournament_deadline_passed = Tournament.objects.create(
            name = "Tournament 0",
            description = "Tournament description",
            club = self.club,
            date = make_aware(datetime.datetime(2020, 12, 25, 12, 0), timezone.utc),
            organizer = self.officer,
            capacity = 2,
            deadline = make_aware(datetime.datetime(2020, 12, 20, 12, 0), timezone.utc),
        )

        self.today = datetime.datetime.today()
        self.yesterday = self.today - datetime.timedelta(days=1)

    def test_is_officer(self):
        self.assertEqual(self.officer_membership.user_type, "OF")

    def test_create_tournament(self):
        before = Tournament.objects.count()
        Tournament.objects.create(
            name = "Tournament 2",
            description = "Tournament description",
            club = self.club,
            date = make_aware(datetime.datetime(2022, 12, 25, 12, 0), timezone.utc),
            organizer = self.officer,
            capacity = 2,
            deadline = make_aware(datetime.datetime(2022, 12, 20, 12, 0), timezone.utc),
        )
        after = Tournament.objects.count()
        self.assertEqual(after, before+1)

    def test_cannot_create_tournaments_with_same_name(self):
        before = Tournament.objects.count()
        with self.assertRaises(Exception) as context:
            Tournament.objects.create(
                name = "Tournament 2",
                description = "Tournament description",
                club = self.club,
                date = make_aware(datetime.datetime(2022, 12, 25, 12, 0), timezone.utc),
                organizer = self.officer,
                capacity = 2,
                deadline = make_aware(datetime.datetime(2022, 12, 20, 12, 0), timezone.utc),
            )
            after = Tournament.objects.count()
            Tournament.objects.create(
                name = "Tournament 2",
                description = "Tournament description",
                club = self.club,
                date = make_aware(datetime.datetime(2022, 12, 25, 12, 0), timezone.utc),
                organizer = self.officer,
                capacity = 2,
                deadline = make_aware(datetime.datetime(2022, 12, 20, 12, 0), timezone.utc),
            )
            after = Tournament.objects.count()
            self.assertEqual(after, before+1)

        self.assertEqual(after, before+1)

    def test_join_tournament_successfully(self):
        before = TournamentParticipation.objects.count()
        join_tournament_message = self.tournament.join_tournament(self.member)
        self.assertEqual(join_tournament_message, "")
        after = TournamentParticipation.objects.count()
        self.assertEqual(before+1, after)

    def test_join_tournament_deadline_passed(self):
        before = TournamentParticipation.objects.count()
        join_tournament_message = self.tournament_deadline_passed.join_tournament(self.member)
        self.assertEqual(join_tournament_message, "You cannot join the tournament once the sign-up deadline has passed.")
        after = TournamentParticipation.objects.count()
        self.assertEqual(before, after)

    def test_join_tournament_not_club_member(self):
        before = TournamentParticipation.objects.count()
        membership = Membership.objects.get(user=self.member, club=self.club)
        membership.leave()
        join_tournament_message = self.tournament.join_tournament(self.member)
        self.assertEqual(join_tournament_message, "You are not a member of this club, you cannot join the tournament.")
        after = TournamentParticipation.objects.count()
        self.assertEqual(before, after)

    def test_join_tournament_as_organizer(self):
        before = TournamentParticipation.objects.count()
        join_tournament_message = self.tournament.join_tournament(self.officer)
        self.assertEqual(join_tournament_message, "You are organizing this tournament, you cannot join it.")
        after = TournamentParticipation.objects.count()
        self.assertEqual(before, after)

    def test_join_tournament_max_capacity_reached(self):
        before = TournamentParticipation.objects.count()
        join_tournament_message = self.tournament.join_tournament(self.member)
        self.assertEqual(join_tournament_message, "")
        join_tournament_message = self.tournament.join_tournament(self.owner)
        self.assertEqual(join_tournament_message, "")
        after = TournamentParticipation.objects.count()
        self.assertEqual(before+2, after)
        new_user = User.objects.create_user(name="Janice Doe", username="janicedoe", email="janicedoe@example.com", password="Password123")
        new_user.save()
        new_user = User.objects.get(username="janicedoe")
        before_memberships = Membership.objects.count()
        (Membership.objects.create(user=new_user, club=self.club, application_status='A', user_type='MB')).save()
        after_memberships = Membership.objects.count()
        self.assertEqual(before_memberships+1, after_memberships)
        self.assertEqual(TournamentParticipation.objects.filter(tournament=self.tournament).count(), self.tournament.capacity)
        join_tournament_message = self.tournament.join_tournament(new_user)
        self.assertEqual(join_tournament_message, "This tournament has reached max capacity, you cannot join it.")
        after_max_capacity = TournamentParticipation.objects.count()
        self.assertEqual(after, after_max_capacity)

    def test_join_tournament_already_signed_up(self):
        before = TournamentParticipation.objects.count()
        join_tournament_message = self.tournament.join_tournament(self.member)
        self.assertEqual(join_tournament_message, "")
        after = TournamentParticipation.objects.count()
        self.assertEqual(before+1, after)
        join_tournament_message = self.tournament.join_tournament(self.member)
        self.assertEqual(join_tournament_message, "You are already signed up to this tournament.")
        after_duplicate_join = TournamentParticipation.objects.count()
        self.assertEqual(after, after_duplicate_join)

    def test_join_tournament_as_coorganizer(self):
        before = TournamentParticipation.objects.count()
        self.tournament.coorganizers.add(self.member)
        join_tournament_message = self.tournament.join_tournament(self.member)
        self.assertEqual(join_tournament_message, "You are organizing this tournament, you cannot join it.")
        after = TournamentParticipation.objects.count()
        self.assertEqual(before, after)

    def test_leave_tournament_successfully(self):
        before = TournamentParticipation.objects.count()
        join_tournament_message = self.tournament.join_tournament(self.member)
        self.assertEqual(join_tournament_message, "")
        after = TournamentParticipation.objects.count()
        self.assertEqual(before+1, after)
        leave_tournament_message = self.tournament.leave_tournament(self.member)
        self.assertEqual(leave_tournament_message, "")
        after_leave = TournamentParticipation.objects.count()
        self.assertEqual(after-1, after_leave)

    def test_leave_tournament_deadline_passed(self):
        before = TournamentParticipation.objects.count()
        TournamentParticipation.objects.create(user=self.member, tournament=self.tournament_deadline_passed)
        after_join = TournamentParticipation.objects.count()
        self.assertEqual(before+1, after_join)
        leave_tournament_message = self.tournament_deadline_passed.leave_tournament(self.member)
        self.assertEqual(leave_tournament_message, "You cannot leave the tournament once the sign-up deadline has passed.")
        after_leave = TournamentParticipation.objects.count()
        self.assertEqual(after_join, after_leave)

    def test_leave_tournament_not_signed_up(self):
        before = TournamentParticipation.objects.count()
        leave_tournament_message = self.tournament.leave_tournament(self.member)
        self.assertEqual(leave_tournament_message, "You are not signed-up for this tournament.")
        after = TournamentParticipation.objects.count()
        self.assertEqual(before, after)

    def test_cancel_tournament_succesfully(self):
        before = Tournament.objects.count()
        cancel_tournament_message = self.tournament.cancel_tournament(self.officer)
        self.assertEqual(cancel_tournament_message, "")
        after = Tournament.objects.count()
        self.assertEqual(before-1, after)

    def test_cancel_tournament_not_organizer(self):
        before = Tournament.objects.count()
        cancel_tournament_message = self.tournament.cancel_tournament(self.member)
        self.assertEqual(cancel_tournament_message, "You are not an organizer for this tournament.")
        after = Tournament.objects.count()
        self.assertEqual(before, after)

    def test_cancel_tournament_after_tournament_start(self):
        before = Tournament.objects.count()
        self.tournament.stage = Tournament.StageTypes.ELIMINATION
        cancel_tournament_message = self.tournament.cancel_tournament(self.officer)
        self.assertEqual(cancel_tournament_message, "This tournament has already started.")
        after = Tournament.objects.count()
        self.assertEqual(before, after)

    def test_cancel_tournament_coorganizer(self):
        before = Tournament.objects.count()
        self.tournament.coorganizers.add(self.member)
        cancel_tournament_message = self.tournament.cancel_tournament(self.member)
        self.assertEqual(cancel_tournament_message, "")
        after = Tournament.objects.count()
        self.assertEqual(before-1, after)


    def test_tournament_different_club_same_name(self):
        club1 = Club.objects.get(name = "Royal Chess Club")
        officer1 = User.objects.get(username="juliedoe")
        before = Tournament.objects.count()
        self.tournament1 = Tournament.objects.create(
            name = "Tournament 1",
            description = "Tournament description",
            club = club1,
            date = make_aware(datetime.datetime(2022, 12, 25, 12, 0), timezone.utc),
            organizer = officer1,
            capacity = 2,
            deadline = make_aware(datetime.datetime(2022, 12, 20, 12, 0), timezone.utc),
        )
        after = Tournament.objects.count()
        self.assertEqual(after, before+1)

    def test_non_member_cannot_join_tournament(self):
        non_member = User.objects.get(username="juliedoe")
        self.assertEqual(self.tournament.join_tournament(non_member), "You are not a member of this club, you cannot join the tournament." )

    def test_organizer_cannot_join_tournament(self):
        with self.assertRaises(Exception):
            tournament.join_tournament(self.officer)

    def test_cannot_leave_never_signed_tournament(self):
        self.assertEqual(self.tournament.leave_tournament(self.member), "You are not signed-up for this tournament." )

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

        for i in range(self.tournament.capacity):
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

    def test_tournament_add_96_participants_invalid_deadline(self):
        tournament2 = Tournament.objects.create(
            name = "Tournament 2",
            description = "Tournament description",
            club = self.club,
            date = None,
            organizer = self.officer,
            capacity = 96,
            deadline = None,
        )
        self.assertEqual(tournament2.stage, Tournament.StageTypes.SIGNUPS_OPEN)

        for i in range(tournament2.capacity):
            User.objects.create(
                username = "user" + str(i),
                email = "user" + str(i) + "@example.com",
                password = "password"
            )
            TournamentParticipation.objects.create(
                tournament = tournament2,
                user = User.objects.get(username = "user" + str(i)),
            )



        tournament2.save()

        # Close Signups
        tournament2.check_tournament_stage_transition()
        self.assertEqual(tournament2.stage, Tournament.StageTypes.SIGNUPS_OPEN)


        tournament2.save()

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
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.GROUP_STAGES)

        for match in Match.objects.filter(tournament = self.tournament):
            self.assertEqual(match.result, Match.MatchResultTypes.WHITE_WIN)

    def test_tournament_96_group_stages_phase_0_black_win(self):
        self.test_tournament_96_group_stages_phase_0_generate_matches()

        for match in Match.objects.filter(tournament = self.tournament):
            match.result = Match.MatchResultTypes.BLACK_WIN
            match.save()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.GROUP_STAGES)

        for match in Match.objects.filter(tournament = self.tournament):
            self.assertEqual(match.result, Match.MatchResultTypes.BLACK_WIN)

    def test_tournament_96_group_stages_phase_0_black_win_invalid_deadline(self):
        self.test_tournament_add_96_participants_invalid_deadline()
        tournament2 = Tournament.objects.get(name="Tournament 2")

        for match in Match.objects.filter(tournament = tournament2):
            match.result = Match.MatchResultTypes.BLACK_WIN
            match.save()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(tournament2.stage, Tournament.StageTypes.SIGNUPS_OPEN)

        for match in Match.objects.filter(tournament = tournament2):
            self.assertEqual(match.result, Match.MatchResultTypes.BLACK_WIN)


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

        for match in Match.objects.filter(tournament = self.tournament):
            self.assertEqual(match.result, Match.MatchResultTypes.WHITE_WIN)


    def test_tournament_96_elimination_generate_matches_white_win(self):
        self.test_tournament_96_group_stages_phase_1_white_win()

        #self.assertEqual(len(self.tournament.competing_players()), 16)
        for i in range(4):
            self.tournament.generate_matches()
            for match in Match.objects.filter(tournament = self.tournament):
                match.result = Match.MatchResultTypes.WHITE_WIN
                match.save()

            self.tournament.check_tournament_stage_transition()


        self.assertEqual(self.tournament.stage, Tournament.StageTypes.FINISHED)

    def test_tournament_add_32_participants(self):
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.SIGNUPS_OPEN)

        for i in range(32):
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

    def test_tournament_32_group_stages_phase_1_generate_matches(self):
        self.test_tournament_add_32_participants()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.GROUP_STAGES)

        self.tournament.generate_matches()

        participants = self.tournament.competing_players()
        group_count = len(participants) // self.tournament.group_size
        match_count = Match.objects.filter(tournament = self.tournament).count()

        self.assertEqual(self.tournament.group_phase, 1)
        self.assertEqual(match_count, group_count * ncr(self.tournament.group_size, 2))

    def test_tournament_32_group_stages_phase_1_white_win(self):
        self.test_tournament_32_group_stages_phase_1_generate_matches()

        for match in Match.objects.filter(tournament = self.tournament):
            match.result = Match.MatchResultTypes.WHITE_WIN
            match.save()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.ELIMINATION)

        for match in Match.objects.filter(tournament = self.tournament):
            self.assertEqual(match.result, Match.MatchResultTypes.WHITE_WIN)

    def test_tournament_32_elimination_generate_matches_white_win(self):
        self.test_tournament_32_group_stages_phase_1_white_win()
        for i in range(4):
            self.tournament.generate_matches()

            for match in Match.objects.filter(tournament = self.tournament):
                match.result = Match.MatchResultTypes.WHITE_WIN
                match.save()

            self.tournament.check_tournament_stage_transition()


        self.assertEqual(self.tournament.stage, Tournament.StageTypes.FINISHED)

    def test_tournament_add_16_participants(self):
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.SIGNUPS_OPEN)

        for i in range(16):
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

    def test_tournament_16_elimination_generate_matches_white_win(self):
        self.test_tournament_add_16_participants()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.ELIMINATION)

        match_counts = [8, 4, 2, 1]
        for i in range(4):
            self.tournament.generate_matches()

            group = Group.objects.get(tournament=self.tournament, phase=i)
            self.assertEqual(Match.objects.filter(tournament = self.tournament, group=group).count(), match_counts[i])

            for match in Match.objects.filter(tournament = self.tournament):
                match.result = Match.MatchResultTypes.WHITE_WIN
                match.save()

            self.tournament.check_tournament_stage_transition()




    def test_tournament_16_elimination_generate_matches_black_win(self):
        self.test_tournament_add_16_participants()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.ELIMINATION)


        while self.tournament.stage == Tournament.StageTypes.ELIMINATION:
            self.tournament.generate_matches()
            for match in Match.objects.filter(tournament = self.tournament):
                match.result = Match.MatchResultTypes.BLACK_WIN
                match.save()

            self.tournament.check_tournament_stage_transition()


        self.assertEqual(self.tournament.stage, Tournament.StageTypes.FINISHED)

    def test_tournament_16_elimination_generate_matches_draw(self):
        self.test_tournament_add_16_participants()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.ELIMINATION)

        #while self.tournament.stage == Tournament.StageTypes.ELIMINATION:
        self.tournament.generate_matches()
        for match in Match.objects.filter(tournament = self.tournament):
            match.result = Match.MatchResultTypes.BLACK_WIN
            match.save()

        self.tournament.check_tournament_stage_transition()

        self.tournament.generate_matches()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.ELIMINATION)

    def test_tournament_16_elimination_generate_matches_invalid_result(self):
        self.test_tournament_add_16_participants()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.ELIMINATION)

        self.tournament.generate_matches()
        for match in Match.objects.filter(tournament = self.tournament):
            match.result = Match.MatchResultTypes.PENDING
            match.save()

        self.tournament.check_tournament_stage_transition()

        self.tournament.generate_matches()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.ELIMINATION)


    def test_tournament_16_elimination_generate_matches_black_win(self):
        self.test_tournament_add_16_participants()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.ELIMINATION)

        match_counts = [8, 4, 2, 1]
        for i in range(4):
            self.tournament.generate_matches()

            group = Group.objects.get(tournament=self.tournament, phase=i)
            self.assertEqual(Match.objects.filter(tournament = self.tournament, group=group).count(), match_counts[i])

            for match in Match.objects.filter(tournament = self.tournament):
                match.result = Match.MatchResultTypes.BLACK_WIN
                match.save()

            self.tournament.check_tournament_stage_transition()


        self.assertEqual(self.tournament.stage, Tournament.StageTypes.FINISHED)


    def test_tournament_add_95_participants(self):
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.SIGNUPS_OPEN)

        for i in range(95):
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

    def test_tournament_95_group_stages_phase_0_generate_matches(self):
        self.test_tournament_add_95_participants()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.GROUP_STAGES)

        self.tournament.generate_matches()

        participants = self.tournament.competing_players()
        group_count = len(participants) // self.tournament.group_size
        match_count = Match.objects.filter(tournament = self.tournament).count()

        self.assertEqual(self.tournament.group_phase, 0)
        self.assertEqual(match_count, group_count * ncr(self.tournament.group_size, 2))

    def test_tournament_95_group_stages_phase_0_white_win(self):
        self.test_tournament_95_group_stages_phase_0_generate_matches()

        for match in Match.objects.filter(tournament = self.tournament):
            match.result = Match.MatchResultTypes.WHITE_WIN
            match.save()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.GROUP_STAGES)

        for match in Match.objects.filter(tournament = self.tournament):
            self.assertEqual(match.result, Match.MatchResultTypes.WHITE_WIN)


    def test_tournament_95_group_stages_phase_1_generate_matches(self):
        self.test_tournament_95_group_stages_phase_0_white_win()

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

    def test_tournament_95_group_stages_phase_1_white_win(self):
        self.test_tournament_95_group_stages_phase_1_generate_matches()

        for match in Match.objects.filter(tournament = self.tournament):
            match.result = Match.MatchResultTypes.WHITE_WIN
            match.save()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.ELIMINATION)

        for match in Match.objects.filter(tournament = self.tournament):
            self.assertEqual(match.result, Match.MatchResultTypes.WHITE_WIN)

    def test_tournament_95_group_stages_phase_1_white_win_invalid_result(self):
        self.test_tournament_95_group_stages_phase_1_generate_matches()

        for match in Match.objects.filter(tournament = self.tournament):
            match.result = Match.MatchResultTypes.PENDING
            match.save()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.GROUP_STAGES)

        for match in Match.objects.filter(tournament = self.tournament):
            self.assertEqual(match.result, Match.MatchResultTypes.PENDING)


    def test_tournament_95_elimination_generate_matches_white_win(self):
        self.test_tournament_95_group_stages_phase_1_white_win()

        for i in range(4):
            self.tournament.generate_matches()

            for match in Match.objects.filter(tournament = self.tournament):
                match.result = Match.MatchResultTypes.WHITE_WIN
                match.save()

            self.tournament.check_tournament_stage_transition()


        self.assertEqual(self.tournament.stage, Tournament.StageTypes.FINISHED)

    def test_tournament_add_31_participants(self):
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.SIGNUPS_OPEN)

        for i in range(31):
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

    def test_tournament_31_group_stages_phase_1_generate_matches(self):
        self.test_tournament_add_31_participants()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.GROUP_STAGES)

        self.tournament.generate_matches()

        participants = self.tournament.competing_players()
        group_count = len(participants) // self.tournament.group_size
        match_count = Match.objects.filter(tournament = self.tournament).count()

        self.assertEqual(self.tournament.group_phase, 1)
        self.assertEqual(match_count, group_count * ncr(self.tournament.group_size, 2))

    def test_tournament_31_group_stages_phase_1_white_win(self):
        self.test_tournament_31_group_stages_phase_1_generate_matches()

        for match in Match.objects.filter(tournament = self.tournament):
            match.result = Match.MatchResultTypes.WHITE_WIN
            match.save()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.ELIMINATION)

        for match in Match.objects.filter(tournament = self.tournament):
            self.assertEqual(match.result, Match.MatchResultTypes.WHITE_WIN)

    def test_tournament_31_elimination_generate_matches_white_win(self):
        self.test_tournament_31_group_stages_phase_1_white_win()
        for i in range(4):
            self.tournament.generate_matches()

            for match in Match.objects.filter(tournament = self.tournament):
                match.result = Match.MatchResultTypes.WHITE_WIN
                match.save()

            self.tournament.check_tournament_stage_transition()


        self.assertEqual(self.tournament.stage, Tournament.StageTypes.FINISHED)

    def test_tournament_add_15_participants(self):
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.SIGNUPS_OPEN)

        for i in range(15):
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

    def test_tournament_15_elimination_generate_matches_white_win(self):
        self.test_tournament_add_15_participants()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.ELIMINATION)

        for i in range(4):
            self.tournament.generate_matches()
            for match in Match.objects.filter(tournament = self.tournament):
                match.result = Match.MatchResultTypes.WHITE_WIN
                match.save()

            self.tournament.check_tournament_stage_transition()


        self.assertEqual(self.tournament.stage, Tournament.StageTypes.FINISHED)

    def test_tournament_16_elimination_generate_matches_white_win_with_draw(self):
        self.test_tournament_add_16_participants()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.ELIMINATION)

        self.tournament.generate_matches()

        for match in Match.objects.filter(tournament = self.tournament):
            match.result = Match.MatchResultTypes.DRAW
            match.save()

        self.tournament.check_tournament_stage_transition()
        self.assertEqual(self.tournament.matches.all().count(), 8)

        self.tournament.generate_matches()

        for match in Match.objects.filter(tournament = self.tournament):
            match.result = Match.MatchResultTypes.WHITE_WIN
            match.save()

        self.tournament.check_tournament_stage_transition()

        self.assertEqual(self.tournament.matches.all().count(), 16)
        self.assertEqual(self.tournament.stage, Tournament.StageTypes.ELIMINATION)


        for i in range(3):
            self.tournament.generate_matches()
            for match in Match.objects.filter(tournament = self.tournament):
                match.result = Match.MatchResultTypes.WHITE_WIN
                match.save()

            self.tournament.check_tournament_stage_transition()


        self.assertEqual(self.tournament.stage, Tournament.StageTypes.FINISHED)
