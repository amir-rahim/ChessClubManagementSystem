from django.db import models
from .users import User
from .clubs import Club


class Tournament(models.Model):
    name = models.CharField(max_length=100, blank=False, unique=True)
    description = models.CharField(max_length=1000, blank=False)
    date = models.DateTimeField(blank=True, null=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=False)
    capacity = models.IntegerField(null=True)
    deadline = models.DateTimeField(null=True)

class TournamentParticipation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=False)
    class Meta:
        unique_together = ("user", "tournament")


class Match(models.Model):
    class MatchResultTypes(models.TextChoices):
        PENDING = 'P'
        WHITE_WIN = 'W'
        DRAW = 'D'
        BLACK_WIN = 'B'

    class StageTypes(models.TextChoices):
        ELIMINATION = 'E'
        GROUP_STAGES = 'G'

    white_player = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name="+")
    black_player = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name="+")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=False, related_name="matches")
    result = models.CharField(max_length=1, choices=MatchResultTypes.choices, default=MatchResultTypes.PENDING)
    stage = models.CharField(max_length=1, choices=StageTypes.choices, default=StageTypes.ELIMINATION)

    MATCH_AWARDS = {
        "WIN": 1,
        "DRAW": 0.5,
        "LOSS": 0
    }

    def get_match_award_for_user(user):
        if user != white_player and user != black_player:
            raise ValueError("User not participant in match")

        if result == MatchResultTypes.PENDING:
            return 0

        if result == MatchResultTypes.DRAW:
            return MATCH_AWARDS["DRAW"]
        else:
            if user == white_player:
                if result == MatchResultTypes.WHITE_WIN:
                    return MATCH_AWARDS["WIN"]
                else:
                    return MATCH_AWARDS["LOSS"]
            else:
                if result == MatchResultTypes.BLACK_WIN:
                    return MATCH_AWARDS["WIN"]
                else:
                    return MATCH_AWARDS["LOSS"]

class Group(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=False, related_name="groups")
    players = models.ManyToManyField(User)

