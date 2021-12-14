"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import User, Club, Membership

class UserModelTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json'
    ]

    def setUp(self):
        self.owner = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name = "Kerbal Chess Club", owner=1)
        self.applicant = User.objects.get(username='janedoe')


    def test_approve_membership(self):
        membership = Membership.objects.create(user=self.applicant, club=self.club)
        self.assertEqual(membership.application_status, Membership.Application.PENDING)
        self.assertEqual(membership.user_type, Membership.UserTypes.NON_MEMBER)
        membership.approve_membership()
        self.assertEqual(membership.application_status, Membership.Application.APPROVED)
        self.assertEqual(membership.user_type, Membership.UserTypes.MEMBER)

    def test_cannot_approve_approved_membership(self):
        membership = Membership.objects.create(user=self.applicant, club=self.club, user_type="MB", application_status="A")
        self.assertEqual(membership.user_type, Membership.UserTypes.MEMBER)
        membership.approve_membership()
        self.assertEqual(membership.application_status, Membership.Application.APPROVED)
        self.assertEqual(membership.user_type, Membership.UserTypes.MEMBER)

    def test_cannot_deny_membership_to_member(self):
        membership = Membership.objects.create(user=self.applicant, club=self.club, user_type="MB", application_status="A")
        membership.deny_membership()
        self.assertEqual(membership.application_status, Membership.Application.APPROVED)
        self.assertEqual(membership.user_type, Membership.UserTypes.MEMBER)

    def test_deny_membership(self):
        membership = Membership.objects.create(user=self.applicant, club=self.club)
        self.assertEqual(membership.application_status, Membership.Application.PENDING)
        self.assertEqual(membership.user_type, Membership.UserTypes.NON_MEMBER)
        membership.deny_membership()
        self.assertEqual(membership.application_status, Membership.Application.DENIED)
        self.assertEqual(membership.user_type, Membership.UserTypes.NON_MEMBER)

    def test_promote_member_to_officer(self):
        membership = Membership.objects.create(user=self.applicant, club=self.club, user_type="MB", application_status="A")
        membership.promote_to_officer()
        self.assertEqual(membership.user_type, Membership.UserTypes.OFFICER)

    def test_cannot_promote_owner_to_officer(self):
        membership = Membership.objects.create(user=self.applicant, club=self.club, user_type="OW", application_status="A")
        membership.promote_to_officer()
        self.assertEqual(membership.user_type, Membership.UserTypes.OWNER)

    def test_demote_officer_to_member(self):
        membership = Membership.objects.create(user=self.applicant, club=self.club, user_type="OF", application_status="A")
        self.assertEqual(membership.user_type, Membership.UserTypes.OFFICER)
        membership.demote_to_member()
        self.assertEqual(membership.user_type, Membership.UserTypes.MEMBER)

    def test_cannot_demote_member_to_member(self):
        membership = Membership.objects.create(user=self.applicant, club=self.club, user_type="MB", application_status="A")
        self.assertEqual(membership.user_type, Membership.UserTypes.MEMBER)
        membership.demote_to_member()
        self.assertEqual(membership.user_type, Membership.UserTypes.MEMBER)

    def test_transfer_ownership_to_officer(self):
        owner_membership = Membership.objects.get(user=self.owner, club=self.club)
        new_membership = Membership.objects.create(user=self.applicant, club=self.club, user_type="OF", application_status="A")

        self.assertEqual(new_membership.user_type, Membership.UserTypes.OFFICER)
        self.assertEqual(Membership.objects.get(user = self.applicant, club = self.club), new_membership)

        owner_membership.transfer_ownership(new_owner = self.applicant)

        new_membership = Membership.objects.get(user=self.applicant, club=self.club)
        self.club = Club.objects.get(name = "Kerbal Chess Club", owner=2)

        self.assertEqual(owner_membership.club.owner, self.applicant)
        self.assertEqual(new_membership.club.owner, self.applicant)
        self.assertEqual(self.club.owner, self.applicant)

    def test_cannot_transfer_ownership_to_member(self):
        owner_membership = Membership.objects.get(user=self.owner, club=self.club)
        membership = Membership.objects.create(user=self.applicant, club=self.club, user_type="MB", application_status="A")
        self.assertEqual(self.club.owner, membership.club.owner)
        with self.assertRaises(Exception):
            owner_membership.transfer_ownership(new_owner = self.applicant)
        self.assertNotEqual(self.club.owner, self.applicant)
        self.assertEqual(self.club.owner, self.owner)

    def test_cannot_demote_owner_to_member(self):
        membership = Membership.objects.get(user=self.owner, club=self.club)
        membership.demote_to_member()
        self.assertEqual(membership.user_type, Membership.UserTypes.OWNER)

    def test_transfer_ownership_and_demote_to_member(self):
        owner_membership = Membership.objects.get(user=self.owner, club=self.club)
        new_membership = Membership.objects.create(user=self.applicant, club=self.club, user_type="OF", application_status="A")
        owner_membership.transfer_ownership(new_owner = self.applicant)
        self.club = Club.objects.get(name = "Kerbal Chess Club", owner=2)
        self.assertEqual(self.club.owner, self.applicant)
        owner_membership.demote_to_member()
        self.assertEqual(owner_membership.user_type, Membership.UserTypes.MEMBER)

    def test_leave_club(self):
        membership = Membership.objects.create(user=self.applicant, club=self.club, user_type="MB", application_status="A")
        membership.leave()
        self.assertEqual(Membership.objects.filter(id = membership.id).count(), 0)

    def test_owner_cannot_leave_club(self):
        owner_membership = Membership.objects.get(user=self.owner, club=self.club)
        owner_membership.leave()
        self.assertEqual(owner_membership.user_type, Membership.UserTypes.OWNER)

class EloRatingTestCase(TestCase):
    def setUp(self):
        self.club = Club.objects.create(name = "Kerbal Chess Club", owner=1)
        self.applicant = User.objects.create(username = "applicant", password = "password")
        self.owner = User.objects.create(username = "owner", password = "password")
        self.applicant_membership = Membership.objects.create(user=self.applicant, club=self.club)
        self.owner_membership = Membership.objects.create(user=self.owner, club=self.club, user_type="OW", application_status="A")

    def test_initial_elo_rating(self):
        self.assertEqual(self.applicant_membership.elo_rating, 1500)
