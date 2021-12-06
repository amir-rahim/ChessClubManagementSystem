"""Unit tests for the TournamentParticipation model."""
from django.test import TestCase
from django.core.exceptions import ValidationError
from clubs.models import User, Club, Tournament, TournamentParticipation
from django.utils.timezone import make_aware
from django.utils import timezone
import datetime

class TournamentParticipationModelTestCase(TestCase):
    """Unit tests for the TournamentParticipation model."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name = "Kerbal Chess Club", owner=1)
        self.officer = User.objects.get(username='janedoe')
        self.tournament = Tournament.objects.create(
            name = "Tournament 1",
            description = "Tournament description",
            club = self.club,
            date = make_aware(datetime.datetime(2021, 12, 25, 12, 0), timezone.utc),
            organizer = self.officer,
            capacity = 16,
            deadline = make_aware(datetime.datetime(2021, 12, 20, 12, 0), timezone.utc),
        )
        self.tournament.save()
        self.tournament = Tournament.objects.get(name="Tournament 1")

    def test_participation_object_creation(self):
        before = TournamentParticipation.objects.count()
        TournamentParticipation.objects.create(user=self.user, tournament=self.tournament)
        after = TournamentParticipation.objects.count()
        self.assertEqual(before+1, after)

    def test_cannot_create_duplicate_objects(self):
        before = TournamentParticipation.objects.count()
        TournamentParticipation.objects.create(user=self.user, tournament=self.tournament)
        after = TournamentParticipation.objects.count()
        self.assertEqual(before+1, after)
        with self.assertRaises(ValidationError):
            TournamentParticipation(user=self.user, tournament=self.tournament).full_clean()

    def test_user_deleted_cascade(self):
        before = TournamentParticipation.objects.count()
        TournamentParticipation.objects.create(user=self.user, tournament=self.tournament)
        after = TournamentParticipation.objects.count()
        self.assertEqual(before+1, after)
        self.user.delete()
        after_deletion = TournamentParticipation.objects.count()
        self.assertEqual(after-1, after_deletion)

    def test_tournament_deleted_cascade(self):
        before = TournamentParticipation.objects.count()
        TournamentParticipation.objects.create(user=self.user, tournament=self.tournament)
        after = TournamentParticipation.objects.count()
        self.assertEqual(before+1, after)
        self.tournament.delete()
        after_deletion = TournamentParticipation.objects.count()
        self.assertEqual(after-1, after_deletion)
