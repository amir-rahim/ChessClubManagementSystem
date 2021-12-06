"""Unit tests of the edit profile form."""
from django import forms
from django.test import TestCase
from clubs.forms import EditProfileForm
from clubs.models import User

class EditProfileTestCase(TestCase):
    """Unit tests of the edit profile form."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json'
    ]

    def setUp(self):
        self.form_input = {
            "name": "John Doe Smith",
            "username": "johndoe123",
            "email": "john@doe.com",
            "public_bio": "Hello! How are you?",
            "chess_experience": "B"
        }

    def test_form_has_necessary_fields(self):
        form = EditProfileForm()
        self.assertIn('username', form.fields)
        self.assertIn('name', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('public_bio', form.fields)
        self.assertIn('chess_experience', form.fields)

    def test_valid_user_form(self):
        form = EditProfileForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['username'] = 'BAD_USERNAME'
        form = EditProfileForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        user = User.objects.get(username='johndoe')
        form = EditProfileForm(instance=user, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(user.username, 'johndoe123')
        self.assertEqual(user.name, 'John Doe Smith')
        self.assertEqual(user.email, 'john@doe.com')
        self.assertEqual(user.public_bio, 'Hello! How are you?')
        self.assertEqual(user.chess_experience, 'B')