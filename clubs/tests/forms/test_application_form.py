"""Unit tests of the membership application form."""
from django import forms
from django.test import TestCase
from clubs.models import User, Club

class ApplicationFormTestCase(TestCase):
    """Unit tests of the membership application form."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='Club1')
        self.form_input = {
            'user': self.user,
            'club': self.club,
        }

    def test_valid_sign_up_form(self):
        #form = MembershipApplicationForm(data=self.form_input)
        #self.assertTrue(form.is_valid())
        pass
