"""Unit tests of the club creation form."""
from django import forms
from django.test import TestCase
from clubs.models import User, Club, Membership
from clubs.forms import ClubCreationForm

class ApplicationFormTestCase(TestCase):
    """Unit tests of the club creation form."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.form_input = {
            'name' : "New club 1",
            'owner' : self.user.pk
        }

    def test_valid_application_form(self):
        form = ClubCreationForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_must_save_correctly(self):
        form = ClubCreationForm(data=self.form_input)
        before_clubs = Club.objects.count()
        before_memberships = Membership.objects.count()
        form.save()
        after_clubs = Club.objects.count()
        after_memberships = Membership.objects.count()

        self.assertEqual(after_clubs, before_clubs + 1)
        self.assertEqual(after_memberships, before_memberships + 1)

    def test_form_has_necessary_fields(self):
        form = ClubCreationForm()
        self.assertIn('name', form.fields)

        club_field = form.fields['name']
        self.assertTrue(isinstance(club_field, forms.CharField))

    def test_form_uses_model_validation(self):
        self.form_input['name'] = None
        form = ClubCreationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_cannot_create_two_clubs_same_name_club(self):
        self.form_input['name'] = "Kerbal Chess Club"
        form = ClubCreationForm(data=self.form_input)

        self.assertFalse(form.is_valid())
