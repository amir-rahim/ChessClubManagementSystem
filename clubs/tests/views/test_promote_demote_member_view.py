"""Tests of the promote demote views"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_query

class PromoteDemoteViewTestCase(TestCase):
    """Tests of the promote and demote views"""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(id=2)
        self.owner = User.objects.get(username='jonathandoe')
        self.member = User.objects.get(username='johndoe')

    def test_promote_user(self):
        self.client.login(username=self.owner.username, password="Password123")
        
        url = reverse('promote_member', kwargs={'club_id': self.club.id, 'user_id': self.member.id})
        response = self.client.get(url)

        member_membership = Membership.objects.get(user=self.member, club=self.club)
        self.assertTrue(member_membership.user_type == Membership.UserTypes.OFFICER)

    def test_promote_user_with_next(self):
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

        self.assertTrue(len(list(get_messages(response.wsgi_request))) == 1)

    def test_promote_error(self):
        self.client.login(username=self.owner.username, password="Password123")
        
        url = reverse('promote_member', kwargs={'club_id': self.club.id, 'user_id': 100})
        response = self.client.get(url)

        self.assertTrue(len(list(get_messages(response.wsgi_request))) == 1)

    def test_demote_user(self):
        self.test_promote_user()

        url = reverse('demote_member', kwargs={'club_id': self.club.id, 'user_id': self.member.id})
        response = self.client.get(url)

        member_membership = Membership.objects.get(user=self.member, club=self.club)
        self.assertTrue(member_membership.user_type == Membership.UserTypes.MEMBER)

    def test_demote_user_with_next(self):
        self.test_promote_user()

        next_url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        url = reverse_with_query('demote_member', {'club_id': self.club.id, 'user_id': self.member.id}, {'next': next_url})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        member_membership = Membership.objects.get(user=self.member, club=self.club)
        self.assertTrue(member_membership.user_type == Membership.UserTypes.MEMBER)
        self.assertRedirects(response, next_url)

    def test_demote_not_permitted(self):
        self.client.login(username=self.member.username, password="Password123")
        
        url = reverse('demote_member', kwargs={'club_id': self.club.id, 'user_id': self.owner.id})
        response = self.client.get(url)

        owner_membership = Membership.objects.get(user=self.owner, club=self.club)
        self.assertTrue(owner_membership.user_type == Membership.UserTypes.OWNER)

        self.assertTrue(len(list(get_messages(response.wsgi_request))) == 1)
       
    def test_demote_error(self):
        self.client.login(username=self.owner.username, password="Password123")
        
        url = reverse('demote_member', kwargs={'club_id': self.club.id, 'user_id': 100})
        response = self.client.get(url)

        self.assertTrue(len(list(get_messages(response.wsgi_request))) == 1)
