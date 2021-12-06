"""Tests of the transfer ownership views"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_query

class TransferOwnershipViewTestCase(TestCase):
    """Tests of the transfer ownerships view"""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(id=2)
        self.owner = User.objects.get(username='jonathandoe')
        self.member = User.objects.get(username='johndoe')

    def test_transfer_ownership(self):
        self.client.login(username=self.owner.username, password="Password123")
        
        url = reverse('transfer_ownership', kwargs={'club_id': self.club.id, 'user_id': self.member.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)

        for message in get_messages(response.wsgi_request):
            self.assertEqual(message.tags, 'success')

        old_owner_membership = Membership.objects.get(user=self.owner, club=self.club)
        old_member_membership = Membership.objects.get(user=self.member, club=self.club)
        self.assertTrue(old_member_membership.user_type == Membership.UserTypes.OWNER)
        self.assertTrue(old_owner_membership == Membership.UserTypes.MEMBER)

    """def test_promote_user_with_next(self):
        self.client.login(username=self.owner.username, password="Password123")
        
        next_url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        url = reverse_with_query('promote_member', {'club_id': self.club.id, 'user_id': self.member.id}, {'next': next_url})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        member_membership = Membership.objects.get(user=self.member, club=self.club)
        self.assertTrue(member_membership.user_type == Membership.UserTypes.OFFICER)
        self.assertRedirects(response, next_url)

    def test_promote_not_permitted(self):
        self.client.login(username=self.member.username, password="Password123")
        
        url = reverse('promote_member', kwargs={'club_id': self.club.id, 'user_id': self.member.id})
        response = self.client.get(url)

        member_membership = Membership.objects.get(user=self.member, club=self.club)
        self.assertTrue(member_membership.user_type == Membership.UserTypes.MEMBER)

        self.assertTrue(len(list(get_messages(response.wsgi_request))) == 1)"""


