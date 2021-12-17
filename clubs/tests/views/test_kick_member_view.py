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

    def test_redirects_when_not_logged_in(self):
        url = reverse('kick_member', kwargs={'club_id': self.club.id, 'user_id': self.user.id})
        redirect_url = reverse_with_query('log_in', query_kwargs={'next': url})
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

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

    def test_successful_kick_with_next(self):
        self.client.login(username=self.owner.username, password="Password123")
        self.assertEqual(self.membership.user_type, 'MB')
        self.assertEqual(self.membership.application_status, 'A')
        before_count = Membership.objects.count()
        next_url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        url = reverse_with_query('kick_member',{'club_id': self.club.id, 'user_id': self.user.id}, {'next': next_url})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
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

    def test_cannot_kick_not_member(self):
        self.client.login(username=self.owner.username, password="Password123")
        non_member = User.objects.get(username="janettedoe")
        before_count = Membership.objects.count()
        url = reverse('kick_member', kwargs={'club_id': self.club.id, 'user_id': non_member.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        after_count = Membership.objects.count()
        self.assertEqual(after_count, before_count)

    def test_member_cannot_kick(self):
        user = User.objects.get(username="janettedoe")
        self.client.login(username=user.username, password="Password123")
        self.assertEqual(self.membership.user_type, 'MB')
        self.assertEqual(self.membership.application_status, 'A')
        before_count = Membership.objects.count()
        url = reverse('kick_member', kwargs={'club_id': self.club.id, 'user_id': self.owner.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        after_count = Membership.objects.count()
        self.assertEqual(after_count, before_count)
