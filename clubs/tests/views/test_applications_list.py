"""Tests of the my_applications view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership


class MyApplicationsViewTestCase(TestCase):
    """Tests of the my_applications view."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.user2 = User.objects.get(username="janedoe")
        self.club1 = Club.objects.get(name="Kerbal Chess Club")
        self.club2 = Club.objects.get(name="Royal Chess Club")
        self.url = reverse('my_applications')

    def test_my_applications_url(self):
        self.assertEqual(self.url,'/my_applications/')

    def test_redirect_user_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_no_application(self):
        self.client.login(username=self.user.username, password='Password123')
        #Create 0 club
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_applications.html')
        list_of_applications = list(response.context['applications_info'])
        self.assertEqual(len(list_of_applications), 0)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

    def test_single_application(self):
        self.client.login(username=self.user.username, password='Password123')
        #Create 1 club
        membership = Membership.objects.create(user=self.user, club=self.club1)
        membership.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_applications.html')
        list_of_applications = list(response.context['applications_info'])
        self.assertEqual(len(list_of_applications), 1)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 0)

    def test_multiple_applications(self):
        self.client.login(username=self.user.username, password='Password123')
        #Create 1 club
        membership1 = Membership.objects.create(user=self.user, club=self.club1)
        membership1.save()
        membership2 = Membership.objects.create(user=self.user, club=self.club2)
        membership2.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_applications.html')
        list_of_applications = list(response.context['applications_info'])
        self.assertEqual(len(list_of_applications), 2)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 0)

    def test_application_from_other_user(self):
        self.client.login(username=self.user.username, password='Password123')
        #Create 1 club
        membership = Membership.objects.create(user=self.user2, club=self.club1)
        membership.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_applications.html')
        list_of_applications = list(response.context['applications_info'])
        self.assertEqual(len(list_of_applications), 0)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
