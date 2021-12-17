"""Tests of the accept_membership and reject_membership functionalities"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_query

class AcceptRejectMembershipTestCase(TestCase):
    """Tests of the accept_membership and reject_membership functionalities"""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.officer = User.objects.get(username="johndoe")
        self.user = User.objects.get(username="janedoe")
        self.membership = Membership(user=self.user, club=self.club)
        self.membership.save()

    def test_accept_membership(self):
        self.client.login(username=self.officer.username, password="Password123")
        self.assertEqual(self.membership.user_type, 'NM')
        self.assertEqual(self.membership.application_status, 'P')
        url = reverse('accept_membership', kwargs={'membership_id': self.membership.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        updated_membership = Membership.objects.get(id=self.membership.id)
        self.assertEqual(updated_membership.user_type, 'MB')
        self.assertEqual(updated_membership.application_status, 'A')

    def test_accept_membership_with_next(self):
        self.client.login(username=self.officer.username, password="Password123")
        self.assertEqual(self.membership.user_type, 'NM')
        self.assertEqual(self.membership.application_status, 'P')
        next_url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        url = reverse_with_query('accept_membership', {'membership_id': self.membership.id}, {'next': next_url})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        updated_membership = Membership.objects.get(id=self.membership.id)
        self.assertEqual(updated_membership.user_type, 'MB')
        self.assertEqual(updated_membership.application_status, 'A')


    def test_reject_membership(self):
        self.client.login(username=self.officer.username, password="Password123")
        self.assertEqual(self.membership.user_type, 'NM')
        self.assertEqual(self.membership.application_status, 'P')
        url = reverse('reject_membership', kwargs={'membership_id': self.membership.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        updated_membership = Membership.objects.get(id=self.membership.id)
        self.assertEqual(updated_membership.user_type, 'NM')
        self.assertEqual(updated_membership.application_status, 'D')

    def test_reject_membership_with_next(self):
        self.client.login(username=self.officer.username, password="Password123")
        self.assertEqual(self.membership.user_type, 'NM')
        self.assertEqual(self.membership.application_status, 'P')
        next_url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        url = reverse_with_query('reject_membership', {'membership_id': self.membership.id}, {'next': next_url})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        updated_membership = Membership.objects.get(id=self.membership.id)
        self.assertEqual(updated_membership.user_type, 'NM')
        self.assertEqual(updated_membership.application_status, 'D')
