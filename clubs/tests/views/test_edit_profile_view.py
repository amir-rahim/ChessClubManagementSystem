"""Tests for the profile view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.forms import EditProfileForm
from clubs.models import User
from clubs.tests.helpers import LogInTester, reverse_with_query

class EditProfileViewTest(TestCase):
    """Test suite for the edit profile view."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.url = reverse('edit_user_profile')
        self.form_input = {
            "name": "John Doe Smith",
            "username": "johndoe123",
            "email": "john@doe.com",
            "public_bio": "Hello! How are you?",
            "chess_experience": "B"
        }

    def test_profile_url(self):
        self.assertEqual(self.url, '/user_profile/edit')

    def test_get_profile(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_user_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))
        self.assertEqual(form.instance, self.user)

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_query('log_in', query_kwargs={'next': self.url})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccessful_profile_update(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['username'] = 'BAD_USERNAME'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_user_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe')
        self.assertEqual(self.user.name, 'John Doe')
        self.assertEqual(self.user.email, 'johndoe@example.com')
        self.assertEqual(self.user.public_bio, "Hello!")
        self.assertEqual(self.user.chess_experience, "G")

    def test_unsuccessful_profile_update_due_to_duplicate(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['username'] = 'janedoe'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_user_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe')
        self.assertEqual(self.user.name, 'John Doe')
        self.assertEqual(self.user.email, 'johndoe@example.com')
        self.assertEqual(self.user.public_bio, "Hello!")
        self.assertEqual(self.user.chess_experience, "G")

    def test_successful_profile_update(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('user_dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_dashboard.html')
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe123')
        self.assertEqual(self.user.name, 'John Doe Smith')
        self.assertEqual(self.user.email, 'john@doe.com')
        self.assertEqual(self.user.public_bio, "Hello! How are you?")
        self.assertEqual(self.user.chess_experience, "B")

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_query('log_in', query_kwargs={'next': self.url})
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)