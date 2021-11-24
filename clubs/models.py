from enum import Enum, auto
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms
from libgravatar import Gravatar

# Create your models here.
class User(AbstractUser):
    """User model used for authentication."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[a-z0-9]([._-](?![._-])|[a-z0-9])*[a-z0-9]$',
                message='Usernames may only contain lowercase characters '
                        'and . _ - but not as '
                        'the first or last character.',
                code='invalid_username'
            )
        ]
    )
    name = models.CharField(max_length=100, blank=False)
    email = models.EmailField(unique=True, blank=False)

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

class Club(models.Model):
    name = models.CharField(max_length=100, blank=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

class Membership(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'club'], name='unique_user_club'),
        ]

    class UserTypes(models.TextChoices):
        NON_MEMBER = 'NM'
        MEMBER = 'MB'
        OFFICER = 'OF'
        OWNER = 'OW'

    class Application(models.TextChoices):
        PENDING = 'P'
        APPROVED = 'A'
        DENIED = 'D'

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True)
    application_status = models.CharField(max_length=10, choices=Application.choices, default=Application.PENDING)
    user_type = models.CharField(max_length=10, choices=UserTypes.choices, default=UserTypes.NON_MEMBER)

    def approveMembership(self):
        if self.user_type == self.UserTypes.NON_MEMBER:
            self.application_status = self.Application.APPROVED
            self.user_type = self.UserTypes.MEMBER
            self.save()

    def denyMembership(self):
        if self.user_type == self.UserTypes.NON_MEMBER:
            self.application_status = self.Application.DENIED
            self.save()

    def promoteToOfficer(self):
        if self.user_type == self.UserTypes.MEMBER:
            self.user_type = self.UserTypes.OFFICER
            self.save()

    def demoteToMember(self):
        if self.user_type == self.UserTypes.OFFICER:
            if Club.objects.filter(name=self.club.name, owner=self.user).count() == 0:
                self.user_type = self.UserTypes.MEMBER
                self.save()

    def transferOwnership(self, new_owner):
        if Membership.objects.get(user = new_owner, club = self.club).user_type == self.UserTypes.OFFICER:
            self.club.owner = new_owner
            self.user_type = self.UserTypes.OFFICER
            new_owner.user_type = self.UserTypes.OWNER
            self.club.save()
            self.save()


class MembershipApplicationForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['club', 'user']
