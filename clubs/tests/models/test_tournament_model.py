"""Unit tests for the Tournament model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, Club, Membership, Tournament, TournamentParticipation
from django.utils.timezone import make_aware
from django.utils import timezone
import datetime

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
        self.member = User.objects.get(username='jonathandoe')
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
