"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, Club, Membership, Tournament
from django.utils.timezone import make_aware
from django.utils import timezone
import datetime

class TournamentModelTestCase(TestCase):
    """Unit tests for the Torunament model."""

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
        self.officer_membership.approveMembership()
        self.officer_membership.promoteToOfficer()


    def test_is_officer(self):
        self.assertEqual(self.officer_membership.user_type, "OF")

    def test_create_tournament(self):
        before = Tournament.objects.count()
        Tournament.objects.create(
            name = "Tournament 1",
            description = "Tournament description",
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
                date = make_aware(datetime.datetime(2021, 12, 25, 12, 0), timezone.utc),
                organizer = self.officer,
                capacity = 2,
                deadline = make_aware(datetime.datetime(2021, 12, 20, 12, 0), timezone.utc),
            )
            after = Tournament.objects.count()
            Tournament.objects.create(
                name = "Tournament 1",
                description = "Tournament description",
                date = make_aware(datetime.datetime(2021, 12, 25, 12, 0), timezone.utc),
                organizer = self.officer,
                capacity = 2,
                deadline = make_aware(datetime.datetime(2021, 12, 20, 12, 0), timezone.utc),
            )
            after = Tournament.objects.count()

        self.assertEqual(after, before+1)
