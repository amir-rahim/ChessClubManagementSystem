from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar

# Create your models here.
class Club(models.Model):
    name = models.CharField(max_length=100, blank=False)


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


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True)
    approved = False
