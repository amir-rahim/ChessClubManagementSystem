"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from clubs.forms import MembershipApplicationForm
from clubs.models import User, Club, Membership
from clubs.tests.helpers import LogInTester, reverse_with_next

class MembershipApplicationViewTestCase(TestCase, LogInTester):
    """Tests of the membership application view."""

    fixtures = [
            'clubs/tests/fixtures/default_users.json',
            'clubs/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.url = reverse('membership_application')
        self.user = User.objects.get(username='johndoe')
        self.applicant = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='Kerbal Chess Club')
        self.form_input = {
            'club' : self.club,
            'user' : self.applicant
        }

    def test_membership_application_url(self):
        self.assertEqual(self.url,'/membership_application/')

    def test_get_membership_application(self):
        self.client.login(username="johndoe", password="Password123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'apply.html')

        form = response.context['form']

        self.assertTrue(isinstance(form, MembershipApplicationForm))
        self.assertFalse(form.is_bound)

    def test_get_membership_application_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_owner_cannot_apply_own_club(self):
        self.client.login(username="johndoe", password="Password123")
        response = self.client.get(self.url)
        form = response.context['form']
        form.cleaned_data = self.form_input
        form.save()
        self.assertFalse(form.is_valid())

    def test_form_shows_all_clubs(self):
        self.client.login(username="johndoe", password="Password123")
        response = self.client.get(self.url)
        form = response.context['form']
        self.assertEqual(len(form['club'].field.queryset), Club.objects.count())

    def test_apply_to_club(self):
        self.client.login(username="janedoe", password="Password123")
        response = self.client.get(self.url)
        form = response.context['form']
        form.cleaned_data = self.form_input
        before_count = Membership.objects.count()
        form.save()
        after_count = Membership.objects.count()
        self.assertEqual(after_count, before_count + 1)

    def test_cannot_apply_twice(self):
        self.client.login(username="janedoe", password="Password123")
        response = self.client.get(self.url)
        form = response.context['form']
        form.cleaned_data = self.form_input
        before_count = Membership.objects.count()
        form.save()
        after_count = Membership.objects.count()
        self.assertEqual(after_count, before_count + 1)

        response = self.client.get(self.url)
        form = response.context['form']
        form.cleaned_data = self.form_input
        form.save()
        self.assertFalse(form.is_valid())
