"""Unit tests of the change password form."""
from django import forms
from django.test import TestCase
from clubs.forms import ChangePasswordForm
from clubs.models import User

class ChangePasswordTestCase(TestCase):
    """Unit tests of the change password form."""

    fixtures = ['clubs/tests/fixtures/default_users.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.form_input = {
            'current_password': 'Password123',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123',
        }

    def test_form_has_necessary_fields(self):
        form = ChangePasswordForm()
        self.assertIn('current_password', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('password_confirmation', form.fields)

    def test_form_has_necessary_fields(self):
        form = ChangePasswordForm()
        self.assertIn('current_password', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('password_confirmation', form.fields)

    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = ChangePasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = ChangePasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'PasswordABC'
        self.form_input['password_confirmation'] = 'PasswordABC'
        form = ChangePasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = ChangePasswordForm(data=self.form_input)
        self.assertFalse(form.is_valid())