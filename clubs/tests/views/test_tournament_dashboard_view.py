"""Tests of the tournament dashboard view"""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership, Tournament, TournamentParticipation
from clubs.tests.helpers import reverse_with_query
from django.utils import timezone
from datetime import datetime

class TournamentDashboardViewTestCase(TestCase):
    """Tests of the tournament dashboard view"""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json',
        'clubs/tests/fixtures/default_tournaments.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.member = User.objects.get(username='johndoe')
        self.organizer = User.objects.get(username='jonathandoe')
        self.tournament = Tournament.objects.get(id=1)
        self.tournament_deadline_passed = Tournament.objects.create(
            name = "Tournament 0",
            description = "Tournament description",
            club = self.club,
            date = timezone.make_aware(datetime(2020, 12, 25, 12, 0), timezone.utc),
            organizer = self.organizer,
            capacity = 2,
            deadline = timezone.make_aware(datetime(2020, 12, 20, 12, 0), timezone.utc),
        )

    def test_get_club_dashboard_view(self):
        self.client.login(username=self.member.username, password="Password123")

        url = reverse('tournament_dashboard', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_dashboard.html')

    def test_club_dashboard_view_redirects_not_logged_in(self):
        url = reverse('tournament_dashboard', kwargs={'tournament_id': self.tournament.id})
        redirect_url = reverse_with_query('log_in', query_kwargs={'next': url})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_join_hidden_to_organizer(self):
        self.client.login(username=self.organizer.username, password="Password123")
        url = reverse('tournament_dashboard', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_dashboard.html')
        self.assertNotContains(response, ">Join Tournament</a>")
        self.assertNotContains(response, '<td>Signups Closed</td>')

    def test_leave_hidden_to_organizer(self):
        self.client.login(username=self.organizer.username, password="Password123")
        url = reverse('tournament_dashboard', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_dashboard.html')
        self.assertNotContains(response, ">Leave Tournament</a>")
        self.assertNotContains(response, '<td>Signups Closed</td>')

    def test_join_hidden_to_signed_up_member(self):
        self.client.login(username=self.member.username, password="Password123")
        TournamentParticipation.objects.create(user=self.member, tournament=self.tournament)
        url = reverse('tournament_dashboard', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_dashboard.html')
        self.assertNotContains(response, ">Join Tournament</a>")
        self.assertNotContains(response, '<td>Signups Closed</td>')

    def test_leave_hidden_to_non_signed_up_member(self):
        self.client.login(username=self.member.username, password="Password123")
        url = reverse('tournament_dashboard', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_dashboard.html')
        self.assertNotContains(response, ">Leave Tournament</a>")
        self.assertNotContains(response, '<td>Signups Closed</td>')

    def test_join_hidden_to_non_signed_up_member_if_capacity_full(self):
        self.client.login(username=self.member.username, password="Password123")
        user2 = User.objects.get(username='janedoe')
        Membership.objects.create(user=user2, club=self.club, application_status='A', user_type='MB')
        user3 = User.objects.get(username='juliedoe')
        Membership.objects.get(user=user3, club=self.club).delete()
        Membership.objects.create(user=user3, club=self.club, application_status='A', user_type='MB')
        tournament_full = Tournament.objects.create(
            name = "Tournament Full",
            description = "Tournament description",
            club = self.club,
            date = timezone.make_aware(datetime(2022, 12, 25, 12, 0), timezone.utc),
            organizer = self.organizer,
            capacity = 2,
            deadline = timezone.make_aware(datetime(2022, 12, 20, 12, 0), timezone.utc),
        )
        TournamentParticipation.objects.create(user=user2, tournament=tournament_full)
        TournamentParticipation.objects.create(user=user3, tournament=tournament_full)
        url = reverse('tournament_dashboard', kwargs={'tournament_id': tournament_full.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_dashboard.html')
        self.assertNotContains(response, ">Join Tournament</a>")
        self.assertNotContains(response, '<td>Signups Closed</td>')

    def test_join_shown_to_non_signed_up_member_if_capacity_not_full(self):
        self.client.login(username=self.member.username, password="Password123")
        url = reverse('tournament_dashboard', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_dashboard.html')
        self.assertContains(response, ">Join Tournament</a>")
        self.assertNotContains(response, '<td>Signups Closed</td>')

    def test_leave_shown_to_signed_up_member(self):
        self.client.login(username=self.member.username, password="Password123")
        TournamentParticipation.objects.create(user=self.member, tournament=self.tournament)
        url = reverse('tournament_dashboard', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_dashboard.html')
        self.assertContains(response, ">Leave Tournament</a>")
        self.assertNotContains(response, '<td>Signups Closed</td>')

    def test_join_hidden_if_tournament_deadline_passed(self):
        self.client.login(username=self.member.username, password="Password123")
        url = reverse('tournament_dashboard', kwargs={'tournament_id': self.tournament_deadline_passed.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_dashboard.html')
        self.assertNotContains(response, ">Join Tournament</a>")
        self.assertContains(response, '<td>Elimination</td>')

    def test_leave_hidden_if_tournament_deadline_passed(self):
        self.client.login(username=self.member.username, password="Password123")
        TournamentParticipation.objects.create(user=self.member, tournament=self.tournament_deadline_passed)
        url = reverse('tournament_dashboard', kwargs={'tournament_id': self.tournament_deadline_passed.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_dashboard.html')
        self.assertNotContains(response, ">Leave Tournament</a>")
        self.assertContains(response, '<td>Elimination</td>')

    def test_cancel_hidden_if_not_organizer(self):
        self.client.login(username=self.member.username, password="Password123")
        url = reverse('tournament_dashboard', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_dashboard.html')
        self.assertNotContains(response, ">Cancel Tournament</a>")

    def test_cancel_hidden_after_tournament_start(self):
        self.client.login(username=self.organizer.username, password="Password123")
        Tournament.objects.filter(pk=self.tournament.pk).update(stage=Tournament.StageTypes.ELIMINATION)
        url = reverse('tournament_dashboard', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_dashboard.html')
        self.assertContains(response, '<td>Elimination</td>')
        self.assertNotContains(response, ">Cancel Tournament</a>")

    def test_cancel_shown_if_organizer_before_tournament_start(self):
        self.client.login(username=self.organizer.username, password="Password123")
        url = reverse('tournament_dashboard', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_dashboard.html')
        self.assertContains(response, ">Cancel Tournament</a>")

    def test_cancel_shown_if_coorganizer(self):
        self.client.login(username=self.member.username, password="Password123")
        self.tournament.coorganizers.add(self.member)
        url = reverse('tournament_dashboard', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_dashboard.html')
        self.assertContains(response, ">Cancel Tournament</a>")
