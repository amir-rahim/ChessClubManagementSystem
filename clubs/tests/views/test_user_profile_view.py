"""Tests of the user_profile view."""
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership


class UserProfileViewTestCase(TestCase):
    """Tests of the user_profile view."""

    fixtures = [
        'clubs/tests/fixtures/default_users.json',
        'clubs/tests/fixtures/default_clubs.json',
        'clubs/tests/fixtures/default_memberships.json',
    ]

    def setUp(self):
        self.membership1 = Membership.objects.get(pk = 1)
        self.membership2 = Membership.objects.get(pk = 2)
        self.membership3 = Membership.objects.get(pk = 3)
        self.membership4 = Membership.objects.get(pk = 4)


        self.url = reverse('user_profile')
        self.data = {'membership' : self.membership1.pk}
        self.data3 = {'membership' : self.membership3.pk}
        self.data4 = {'membership' : self.membership4.pk}


    def test_post_request(self):
        self.client.login( username = self.membership1.user, password =  'Password123')
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)

    def test_user_profile_viewed_from_member(self):
        self.client.login( username = self.membership3.user, password =  'Password123')
        response = self.client.post(self.url, self.data3)
        self.assertContains(response, "<h4 class=\"cover-text\">Name: </h4>" )
        self.assertContains(response, "<h4 class=\"cover-text\">Email: </h4>" )
        self.assertNotContains(response, "<h4 class=\"cover-text\">Chess Experience: </h4>" )
        self.assertContains(response, "<h4 class=\"cover-text\">Bio: </h4>" )
        self.assertNotContains(response, "<h2 class=\"cover-heading\">Contact Details</h2>" )
        self.assertNotContains(response, "<a href= '"+ self.url +"' class=\"btn btn-lg btn-secondary\"> Edit Profile </a>")


def test_user_profile_viewed_from_owmer(self):
        self.client.login( username = self.membership1.user, password =  'Password123')
        response = self.client.post(self.url, self.data)
        self.assertContains(response, "<h4 class=\"cover-text\">Name: </h4>" )
        self.assertContains(response, "<h4 class=\"cover-text\">Email: </h4>" )
        self.assertContains(response, "<h4 class=\"cover-text\">Chess Experience: </h4>" )
        self.assertContains(response, "<h4 class=\"cover-text\">Bio: </h4>" )
        self.assertContains(response, "<h2 class=\"cover-heading\">Contact Details</h2>" )
        self.assertNotContains(response, "<a href= '"+ self.url +"' class=\"btn btn-lg btn-secondary\"> Edit Profile </a>")

def test_user_profile_viewed_from_officer(self):
        self.client.login( username = self.membership4.user, password =  'Password123')
        response = self.client.post(self.url, self.data4)
        self.assertContains(response, "<h4 class=\"cover-text\">Name: </h4>" )
        self.assertContains(response, "<h4 class=\"cover-text\">Email: </h4>" )
        self.assertContains(response, "<h4 class=\"cover-text\">Chess Experience: </h4>" )
        self.assertContains(response, "<h4 class=\"cover-text\">Bio: </h4>" )
        self.assertContains(response, "<h2 class=\"cover-heading\">Contact Details</h2>" )
        self.assertNotContains(response, "<a href= '"+ self.url +"' class=\"btn btn-lg btn-secondary\"> Edit Profile </a>")
