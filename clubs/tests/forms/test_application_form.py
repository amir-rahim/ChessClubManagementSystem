"""Unit tests of the membership application form."""
from django import forms
from django.test import TestCase
from clubs.models import User, Club, MembershipApplicationForm, Membership
#from clubs.forms import MembershipApplicationForm

class ApplicationFormTestCase(TestCase):
    """Unit tests of the membership application form."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='Kerbal Chess Club')
        self.form_input = {
            'club' : self.club,
            'user' : self.user
        }

    def test_valid_application_form(self):
        form = MembershipApplicationForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_valid_initial_data(self):
        form = MembershipApplicationForm(initial = {'user': self.user})
        print(form.initial['user'].id)

    def test_form_has_necessary_fields(self):
        form = MembershipApplicationForm()
        self.assertIn('club', form.fields)

        club_field = form.fields['club']
        self.assertTrue(isinstance(club_field, forms.ModelChoiceField))

    def test_form_uses_model_validation(self):
        self.form_input['club'] = None
        form = MembershipApplicationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = MembershipApplicationForm(data=self.form_input)
        before_count = Membership.objects.count()
        form.save()
        after_count = Membership.objects.count()

        self.assertEqual(after_count, before_count + 1)

    def test_cannot_apply_multiple_times_same_club(self):
        form = MembershipApplicationForm(data=self.form_input)
        before_count = Membership.objects.count()
        form.save()
        after_count = Membership.objects.count()
        self.assertEqual(after_count, before_count + 1)
        form = MembershipApplicationForm(data=self.form_input)
        self.assertFalse(form.is_valid())
