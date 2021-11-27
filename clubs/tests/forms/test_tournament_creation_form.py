"""Unit tests of the membership application form."""
from django import forms
from django.test import TestCase
from clubs.models import User, Club, Membership, Tournament
from clubs.forms import TournamentCreationForm
from django.utils.timezone import make_aware
from django.utils import timezone
import datetime

class TournamentCreationFormTestCase(TestCase):
    """Unit tests of the membership application form."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(name = "Kerbal Chess Club", owner=1)
        self.officer = User.objects.get(username='janedoe')
        self.officer_membership = Membership.objects.create(user = self.officer, club = self.club, personal_statement = "---")
        self.officer_membership.approveMembership()
        self.officer_membership.promoteToOfficer()
        self.form_input = {
            'name': "Tournament 1",
            'description': "Tournament description",
            'club': self.club,
            'date': make_aware(datetime.datetime(2021, 12, 25, 12, 0), timezone.utc),
            'organizer': self.officer,
            'capacity': 2,
            'deadline': make_aware(datetime.datetime(2021, 12, 20, 12, 0), timezone.utc),
        }

    def test_valid_application_form(self):
        form = TournamentCreationForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = TournamentCreationForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('organizer', form.fields)
        self.assertIn('date', form.fields)
        self.assertIn('club', form.fields)
        self.assertIn('deadline', form.fields)
        self.assertIn('capacity', form.fields)


        self.assertTrue(isinstance(form.fields['name'], forms.CharField))
        self.assertTrue(isinstance(form.fields['description'], forms.CharField))
        self.assertTrue(isinstance(form.fields['organizer'], forms.ModelChoiceField))
        self.assertTrue(isinstance(form.fields['club'], forms.ModelChoiceField))
        self.assertTrue(isinstance(form.fields['date'], forms.DateTimeField))
        self.assertTrue(isinstance(form.fields['deadline'], forms.DateTimeField))
        self.assertTrue(isinstance(form.fields['capacity'], forms.IntegerField))

    def test_form_uses_model_validation(self):
        self.form_input['club'] = None
        form = TournamentCreationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = TournamentCreationForm(data=self.form_input)
        before_count = Tournament.objects.count()
        self.assertTrue(form.is_valid())
        form.save()
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count + 1)

    def test_capacity_cannot_be_smaller_than_2(self):
        self.form_input['capacity'] = 1
        form = TournamentCreationForm(data=self.form_input)
        before_count = Tournament.objects.count()
        self.assertFalse(form.is_valid())
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count)

    def test_capacity_cannot_be_greater_than_96(self):
        self.form_input['capacity'] = 97
        form = TournamentCreationForm(data=self.form_input)
        before_count = Tournament.objects.count()
        self.assertFalse(form.is_valid())
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count)

    def test_deadline_cannot_be_after_date(self):
        self.form_input['deadline'] = make_aware(datetime.datetime(2021, 12, 27, 12, 0), timezone.utc)
        form = TournamentCreationForm(data=self.form_input)
        before_count = Tournament.objects.count()
        self.assertFalse(form.is_valid())
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count)
