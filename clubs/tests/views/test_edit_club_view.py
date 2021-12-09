"""Tests for the profile view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.forms import EditClubDetailsForm
from clubs.models import User, Club
from clubs.tests.helpers import LogInTester, reverse_with_query

class EditClubDetailsTest(TestCase):
    """Test suite for the edit club details view."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='Kerbal Chess Club')
        self.url = reverse('edit_club', kwargs={'club_id':self.club.id})
        self.form_input = {
            'name' : "New club 1",
            'owner' : self.user.id,
            'location': "London",
            'mission_statement' : "Hello!",
            'description' : "This is a new club!"
        }

    def test_edit_club_url(self):
        self.assertEqual(self.url, '/club/1/edit')

    def test_get_club(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditClubDetailsForm))
        self.assertEqual(form.instance, self.club)

    def test_club_edit_redirects_when_not_owner(self):
        redirect_url = reverse_with_query('log_in', query_kwargs={'next': self.url})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccessful_club_update_due_to_duplicate(self):
        self.client.login(username='johndoe', password='Password123')
        self.form_input['name'] = 'Royal Chess Club'
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditClubDetailsForm))
        self.assertTrue(form.is_bound)
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, 'Kerbal Chess Club')
        self.assertEqual(self.club.location, 'New York')
        self.assertEqual(self.club.mission_statement, "Best Club in the World!")
        self.assertEqual(self.club.description, "Welcome to our club! Who keeps the best players around!")

    def test_unsuccessful_profile_update_due_not_owner(self):
        self.client.login(username='jonathandoe', password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_dashboard.html')
        #self.assertTrue(isinstance(response.context['form'], EditClubDetailsForm))
        #self.assertTrue(response.context['form'].is_bound)
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, 'Kerbal Chess Club')
        self.assertEqual(self.club.location, 'New York')
        self.assertEqual(self.club.mission_statement, "Best Club in the World!")
        self.assertEqual(self.club.description, "Welcome to our club! Who keeps the best players around!")

    def test_unsuccessful_profile_update_due_not_in_club(self):
        self.client.login(username='janedoe', password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_dashboard.html')
        #self.assertTrue(isinstance(response.context['form'], EditClubDetailsForm))
        #self.assertTrue(response.context['form'].is_bound)
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, 'Kerbal Chess Club')
        self.assertEqual(self.club.location, 'New York')
        self.assertEqual(self.club.mission_statement, "Best Club in the World!")
        self.assertEqual(self.club.description, "Welcome to our club! Who keeps the best players around!")

    def test_successful_profile_update(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_dashboard', kwargs={'club_id':self.club.pk})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club_dashboard.html')
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, 'New club 1')
        self.assertEqual(self.club.location, 'London')
        self.assertEqual(self.club.mission_statement, "Hello!")
        self.assertEqual(self.club.description, "This is a new club!")

    def test_edit_club_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_query('log_in', query_kwargs={'next': self.url})
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
