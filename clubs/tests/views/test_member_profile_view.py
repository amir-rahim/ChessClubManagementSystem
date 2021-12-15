"""Tests of the user_profile view."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils.timezone import make_aware
from django.utils import timezone
import datetime
from clubs.models import User, Club, Membership, Tournament, TournamentParticipation


class MemberProfileViewTestCase(TestCase):
    """Tests of the member_profile view."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json',
        'clubs/tests/fixtures/default_tournaments.json'
    ]

        
    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.user = User.objects.get(username='johndoe')
        self.officer = User.objects.get(username='jonathandoe')
        self.non_member = User.objects.get(username='janedoe')
        self.tournament = Tournament.objects.get(id=1)

    def test_get_member_profile_view(self):
        self.client.login(username=self.user.username, password="Password123")

        user_membership = Membership.objects.get(user=self.user, club=self.club)
        url = reverse('member_profile', kwargs={'membership_id': user_membership.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_profile.html')
        

    def test_member_profile_viewed_from_non_member(self):
        self.client.login(username=self.non_member, password="Password123")

        user_membership = Membership.objects.get(user=self.user, club=self.club)
        url = reverse('member_profile', kwargs={'membership_id': user_membership.id})
        response = self.client.get(url)

        self.assertRedirects(response, reverse('user_dashboard'))
        for message in get_messages(response.wsgi_request):
            self.assertEqual(message.tags, 'danger')

    def test_member_profile_doesnt_exist(self):
        self.client.login(username=self.user.username, password="Password123")

        url = reverse('member_profile', kwargs={'membership_id': 99999})
        response = self.client.get(url)

        self.assertRedirects(response, reverse('user_dashboard'))
        for message in get_messages(response.wsgi_request):
            self.assertEqual(message.tags, 'danger')

    def test_member_profile_context(self):
        self.client.login(username=self.user.username, password="Password123")

        user_membership = Membership.objects.get(user=self.user, club=self.club)
        tournament_participation = TournamentParticipation(user=self.user, tournament=self.tournament)
        tournament_participation.save()

        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=1)

        self.tournament.deadline = make_aware(yesterday, timezone.utc)
        self.tournament.save()
        self.tournament.check_tournament_stage_transition()
        self.tournament.date = make_aware(yesterday, timezone.utc)
        self.tournament.save()
        self.tournament.check_tournament_stage_transition()

        self.tournament.generate_matches()

        url = reverse('member_profile', kwargs={'membership_id': user_membership.id})
        response = self.client.get(url)

        self.assertEqual(response.context['membership'], user_membership)
        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['user'], self.user)
        self.assertEqual(response.context['tournaments'], [self.tournament])
        self.assertEqual(len(response.context['matches']), 1)
        
