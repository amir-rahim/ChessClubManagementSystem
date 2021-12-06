"""Testing of the kick member functionalities"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_query

class KickMemberTestCase(TestCase):
    """Testing of the kick member functionalities"""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(id=2)
        self.owner = User.objects.get(username="jonathandoe")
        self.user = User.objects.get(username="johndoe")
        self.membership = Membership.objects.get(user=self.user, club=self.club)

    def test_successful_kick(self):
        self.client.login(username=self.owner.username, password="Password123")
        self.assertEqual(self.membership.user_type, 'MB')
        self.assertEqual(self.membership.application_status, 'A')
        before_count = Membership.objects.count()
        url = reverse('kick_member', kwargs={'club_id': self.club.id, 'user_id': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        after_count = Membership.objects.count()
        self.assertEqual(after_count + 1, before_count)

    def test_unsuccessful_kick(self):
        self.client.login(username=self.user.username, password="Password123")
        self.assertEqual(self.membership.user_type, 'MB')
        self.assertEqual(self.membership.application_status, 'A')
        before_count = Membership.objects.count()
        url = reverse('kick_member', kwargs={'club_id': self.club.id, 'user_id': self.owner.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        after_count = Membership.objects.count()
        self.assertEqual(after_count, before_count)
        