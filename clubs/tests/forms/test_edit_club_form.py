"""Unit tests of the edit profile form."""
from django import forms
from django.test import TestCase
from clubs.forms import EditClubDetailsForm
from clubs.models import User, Club

class EditClubTestCase(TestCase):
    """Unit tests of the edit club form."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.form_input = {
            'name' : "New club 1",
            'owner' : self.user.id,
            'location': "London",
            'mission_statement' : "Hello!",
            'description' : "This is a new club!"
        }

    def test_form_has_necessary_fields(self):
        form = EditClubDetailsForm()
        self.assertIn('name', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('mission_statement', form.fields)
        self.assertIn('description', form.fields)

    def test_valid_edit_club_form(self):
        form = EditClubDetailsForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['name'] = '_BAD_USERNAME'
        form = EditClubDetailsForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        club = Club.objects.get(name='Kerbal Chess Club')
        form = EditClubDetailsForm(instance=club, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(club.name, 'New club 1')
        self.assertEqual(club.location, 'London')
        self.assertEqual(club.owner, self.user)
        self.assertEqual(club.mission_statement, 'Hello!')
        self.assertEqual(club.description, 'This is a new club!')
        self.assertEqual(before_count, after_count)