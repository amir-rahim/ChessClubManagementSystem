"""Unit tests of the membership application form."""
from django import forms
from django.test import TestCase
from clubs.models import User, Club
from clubs.forms import MembershipApplicationForm

class ApplicationFormTestCase(TestCase):
    """Unit tests of the membership application form."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        ##self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='Kerbal Chess Club')
        self.form_input = {
            'club' : self.club
        }

    def test_valid_application_form(self):
        form = MembershipApplicationForm(data=self.form_input)
        self.assertTrue(form.is_valid())
