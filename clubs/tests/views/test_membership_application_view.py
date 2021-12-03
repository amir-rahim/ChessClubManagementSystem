"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership
from clubs.forms import MembershipApplicationForm
from clubs.tests.helpers import LogInTester, reverse_with_next

class MembershipApplicationViewTestCase(TestCase, LogInTester):
    """Tests of the membership application view."""

    fixtures = [
            'clubs/tests/fixtures/default_users.json',
            'clubs/tests/fixtures/default_clubs.json',
            'clubs/tests/fixtures/default_memberships.json'
    ]

    def setUp(self):
        self.url = reverse('membership_application')
        self.user = User.objects.get(username='johndoe')
        self.applicant = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='Royal Chess Club')
        self.form_input = {
            'club' : [self.club.pk],
            'user' : [self.applicant.pk],
            'personal_statement': "Hello"
        }


    def test_membership_application_url(self):
        self.assertEqual(self.url,'/membership_application/')

    def test_get_membership_application(self):
        self.client.login(username="janedoe", password="Password123")
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

    def test_not_valid_membership_application(self):
        self.client.login(username="janedoe", password="Password123")
        self.form_input.pop('personal_statement')
        before_count = Membership.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Membership.objects.count()
        self.assertEqual(after_count, before_count)

    def test_canno_fill_personal_statement_with_spaces(self):
        self.client.login(username="janedoe", password="Password123")
        self.form_input['personal_statement'] = "     "
        before_count = Membership.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Membership.objects.count()
        self.assertEqual(after_count, before_count)

    def test_redirects_when_applied_to_every_club(self):
        for club in Club.objects.all():
            if Membership.objects.filter(user = self.applicant, club = club).count() <= 0:
                Membership.objects.create(user = self.applicant, club = club)
        self.client.login(username="janedoe", password="Password123")
        response = self.client.get(self.url)
        response_url = reverse('user_dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_apply_to_club(self):
        self.client.login(username="janedoe", password="Password123")
        before_count = Membership.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Membership.objects.count()
        self.assertEqual(after_count, before_count + 1)
