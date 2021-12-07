"""Tests of the leave club view"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_query

class LeaveClubViewTestCase(TestCase):
    """Tests of the leave club views"""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(id=2)
        self.owner = User.objects.get(username='jonathandoe')
        self.member = User.objects.get(username='johndoe')

    def test_leave_club(self):
        self.client.login(username=self.member.username, password="Password123")
        
        url = reverse('leave_club', kwargs={'club_id': self.club.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Membership.objects.filter(user=self.member, club=self.club).exists())

    def test_leave_club_owner(self):
        self.client.login(username=self.owner.username, password="Password123")
        
        url = reverse('leave_club', kwargs={'club_id': self.club.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 500)
        self.assertTrue(Membership.objects.filter(user=self.owner, club=self.club).exists())

    def test_leave_club_error(self):
        self.client.login(username=self.member.username, password="Password123")
        
        url = reverse('leave_club', kwargs={'club_id': 100})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 500)
        self.assertTrue(Membership.objects.filter(user=self.member, club=self.club).exists())
        self.assertFalse(len(list(get_messages(response.wsgi_request))) == 0)

    def test_leave_club_with_next(self):
        self.client.login(username=self.member.username, password="Password123")
        
        next_url = reverse('user_dashboard')
        url = reverse_with_query('leave_club', {'club_id': self.club.id}, {'next': next_url})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Membership.objects.filter(user=self.member, club=self.club).exists())
        self.assertRedirects(response, next_url)
 
    def test_leave_club_error_with_previous(self):
        self.client.login(username=self.member.username, password="Password123")

        next_url = reverse('user_dashboard')
        previous_url = reverse('club_dashboard', kwargs={'club_id': self.club.id})
        url = reverse_with_query('leave_club', {'club_id': 100}, {'next': next_url, 'previous': previous_url})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Membership.objects.filter(user=self.member, club=self.club).exists())
        self.assertFalse(len(list(get_messages(response.wsgi_request))) == 0)
        self.assertRedirects(response, previous_url)
 


