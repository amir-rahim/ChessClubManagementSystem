from django.db import models
from django.core.validators import RegexValidator
from django.db import models
from django import forms
from libgravatar import Gravatar
from django.utils import timezone
from datetime import datetime

from .users import User


class Club(models.Model):
    name = models.CharField(
        max_length=100,
        blank=False,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z][a-zA-Z0-9 ]+',
            message='Club name must start with a letter and contain only letters, number, and spaces.'
        )])
"""Attributes of a club."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    location=models.CharField(max_length=100, blank=False)
    mission_statement=models.CharField(max_length=200, blank=False)
    description=models.CharField(max_length=500, blank=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            Membership.objects.get(club = self, user = self.owner)
        except:
            Membership.objects.create(
                user=self.owner,
                club=self,
                application_status=Membership.Application.APPROVED,
                user_type=Membership.UserTypes.OWNER,
                personal_statement = "-"
            )

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
"""Attributes of a use in the club"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=False)
    personal_statement = models.CharField(max_length=500, blank=False)
    application_status = models.CharField(max_length=10, choices=Application.choices, default=Application.PENDING)
    user_type = models.CharField(max_length=10, choices=UserTypes.choices, default=UserTypes.NON_MEMBER)
    
    highest_elo_rating = models.IntegerField(default=1000)
    lowest_elo_rating = models.IntegerField(default=1000)

    def approve_membership(self):
    """Application is approved and user becomes a memeber of the club."""
        if self.user_type == self.UserTypes.NON_MEMBER:
            self.application_status = self.Application.APPROVED
            self.user_type = self.UserTypes.MEMBER
            self.save()

    def deny_membership(self):
    """Application is denied and doesn't proceed."""
        if self.user_type == self.UserTypes.NON_MEMBER:
            self.application_status = self.Application.DENIED
            self.save()

    def promote_to_officer(self):
    """Member promoted to officer type of membership."""
        if self.user_type == self.UserTypes.MEMBER:
            self.user_type = self.UserTypes.OFFICER
            self.save()

    def demote_to_member(self):
    """Officer demoted into member type of membership."""
        if self.user_type == self.UserTypes.OFFICER and Club.objects.filter(name=self.club.name, owner=self.user).count() == 0:
                self.user_type = self.UserTypes.MEMBER
                self.save()

    def transfer_ownership(self, new_owner):
    """Previous owner transfers ownership, new owner gains ownership powers."""
        new_owner_membership = Membership.objects.get(user = new_owner, club = self.club)
        if new_owner_membership is None:
            raise Exception("User is not a member of the club.")
        else:
            if new_owner_membership.user_type == self.UserTypes.OFFICER:
                self.club.owner = new_owner
                self.user_type = self.UserTypes.OFFICER
                new_owner_membership.user_type = self.UserTypes.OWNER

                new_owner_membership.save()
                self.club.save()
                self.save()
            else:
                raise Exception("Member must be an officer to transfer ownership.")


    def kick_member(self):
    """User is removed from the club and deleted from the database."""
        if self.user_type in [self.UserTypes.MEMBER, self.UserTypes.OFFICER]:
            self.delete()
            return True
        return False

    def leave(self):
     """User is leaves the club and deleted from the database."""
        if self.user_type in [self.UserTypes.MEMBER, self.UserTypes.OFFICER]:
            self.delete()
            return True
        return False

    # Define which user types share the same identities
    USER_TYPE_IDENTITIES = {
        UserTypes.NON_MEMBER: [UserTypes.NON_MEMBER],
        UserTypes.MEMBER: [UserTypes.MEMBER]
    }

    # An Officer is a Member and an Officer
    USER_TYPE_IDENTITIES[UserTypes.OFFICER] = USER_TYPE_IDENTITIES[UserTypes.MEMBER] + [
        UserTypes.OFFICER
    ]

    # An Owner is a Member, an Officer, and an Owner
    USER_TYPE_IDENTITIES[UserTypes.OWNER] = USER_TYPE_IDENTITIES[UserTypes.OFFICER] + [
        UserTypes.OWNER
    ]

    def get_user_types(self):
        return self.USER_TYPE_IDENTITIES[self.user_type]


    USER_TYPE_NAMES = {
        UserTypes.NON_MEMBER: "a Non-Member",
        UserTypes.MEMBER: "a Member",
        UserTypes.OFFICER: "an Officer",
        UserTypes.OWNER: "the Owner"
    }

    def get_user_type_name(self):
        return self.USER_TYPE_NAMES[self.user_type]


    def calculate_new_elo_rating(self, rating_a, player_a, rating_b, player_b, match):
        """Calculations of elo rating"""
        expected_score_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
        expected_score_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))

        new_rating_a = rating_a + 32 * (match.get_match_award_for_user(player_a) - expected_score_a)
        new_rating_b = rating_b + 32 * (match.get_match_award_for_user(player_b) - expected_score_b)

        """if match.result == Match.MatchResultTypes.WHITE_WIN:
            new_rating_a = rating_a + 32 * (1 - expected_score_a)
            new_rating_b = rating_b + 32 * (0 - expected_score_b)
        elif match.result == Match.MatchResultTypes.BLACK_WIN:
            new_rating_a = rating_a + 32 * (0 - expected_score_a)
            new_rating_b = rating_b + 32 * (1 - expected_score_b)
        elif match.result == Match.MatchResultTypes.DRAW:
            new_rating_a = rating_a + 32 * (0.5 - expected_score_a)
            new_rating_b = rating_b + 32 * (0.5 - expected_score_b)"""

        return new_rating_a, new_rating_b

    @property
    def elo_rating(self, date):
        """Set default elo to 1000 and update elo"""
        if not date:
            date = timezone.now()

        matches = Match.objects.filter(Q(white_player = self.user) | Q(black_player = self.user)).filter(date__lte=date).order_by('date')

        current_rating = 1000
        for match in match:
            if match.white_player == self.user:
                player_b = match.black_player
            else:
                player_b = match.white_player

            player_b_membership = Membership.objects.get(user = player_b, club = self.club)
            rating_b = player_b_membership.elo_rating(date)

            current_rating = self.calculate_new_elo_rating(current_rating, self.user, rating_b, player_b, match)[0]

        if current_rating < self.lowest_elo_rating:
            self.lowest_elo_rating = current_rating
            self.save()
        elif current_rating > self.highest_elo_rating:
            self.highest_elo_rating = current_rating
            self.save()

        return current_rating
