from django.db import models
from django.utils import timezone
from django.db.models import Q
import datetime
from .users import User
from .clubs import Club
import random
import itertools


class Tournament(models.Model):
    class StageTypes(models.TextChoices):
        SIGNUPS_OPEN = 'S'
        SIGNUPS_CLOSED = 'C'
        ELIMINATION = 'E'
        GROUP_STAGES = 'G'
        FINISHED = 'F'

    name = models.CharField(max_length=100, blank=False, unique=True)
    description = models.CharField(max_length=1000, blank=False)
    date = models.DateTimeField(blank=True, null=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=False)
    capacity = models.IntegerField(null=True)
    deadline = models.DateTimeField(null=True)
    stage = models.CharField(max_length=1, choices=StageTypes.choices, default=StageTypes.SIGNUPS_OPEN)

    def generate_elimination_matches(self):
        # TODO: Check all matches completed 

        # Generate groups from each stage
        group = None
        if not self.matches.filter(stage=Match.MatchStageTypes.ELIMINATION).exists():
            competing_players = []
            for group in self.groups.all():
                group_results = group.get_group_results()

                for group_result in sorted(group_results, key=group_results.get, reverse=True)[:2]:
                    competing_players.append(group_result)

            group = Group(tournament=self, name='Elimination 1', elimination_stage=0)
            group.save()
            for competing_player in competing_players:
                group.players.add(competing_player)
        else:
            last_competing_group = Group.objects.filter(tournament=self).latest('elimination_stage')
            last_competing_players = last_competing_group.players.all()

            last_matches = self.matches.filter(stage=Match.MatchStageTypes.ELIMINATION, group=last_competing_group)

            players_within_matches = []
            for last_match in last_matches:
                players_within_matches.append(last_match.white_player)
                players_within_matches.append(last_match.black_player)

            competing_players = []

            # Add bye player to competitors based on player not within matches
            for last_competing_player in last_competing_players:
                if not last_competing_player in players_within_matches:
                    competing_players.append(last_competing_player)

            for match in self.matches.filter(stage=Match.MatchStageTypes.ELIMINATION, group=last_competing_group):
                if match.result == Match.MatchResultTypes.WHITE_WIN:
                    competing_players.append(match.white_player)
                elif match.result == Match.MatchResultTypes.BLACK_WIN:
                    competing_players.append(match.black_player)

                # TODO: Change functionality to reschedule match
                elif match.result == Match.MatchResultTypes.DRAW:
                    competing_players.append(match.white_player)
                    competing_players.append(match.black_player)

            group_index = last_competing_group.elimination_stage + 1
            group = Group(tournament=self, name=f'Elimination {group_index+1}', elimination_stage=group_index)
            group.save()
            for competing_player in competing_players:
                group.players.add(competing_player)


        print(f"On group {group.elimination_stage}")
        print(group.players.count())

        group_players = list(group.players.all())

        if len(group_players) % 2 != 0:
            bye_player = group.players[-1]
            group_players.remove(bye_player)

        it = iter(group_players)
        players_of_matches = zip(it,it)

        for players_of_match in players_of_matches: 
            match = Match(white_player=players_of_match[0], 
                          black_player=players_of_match[1], 
                          tournament=self,
                          group=group,
                          stage=Match.MatchStageTypes.ELIMINATION)
            match.save()
        

    def generate_group_stage_matches(self):
        # Generate group stage matches
        for group in self.groups.all():
            # TODO: Generate matches for each group
            for white_player, black_player in itertools.combinations(group.players.all(), 2):
                match = Match(tournament=self, white_player=white_player, black_player=black_player, stage=Match.MatchResultTypes.PENDING)
                match.save()

    def generate_group_stages(self):
        # Generate group stages
        participants = list(self.participants.all())
        #random.shuffle(participants)

        group_size = 4 if self.capacity <= 32 else 6
        group_count = self.participants.count() // group_size

        for i in range(group_count):
            group_letter = chr(ord('@')+(i+1))
            group = Group(tournament=self, name=f'Group {group_letter}')
            group.save()

            for j in range(group_size):
                group.players.add(participants[i * group_size + j].user)

            group.save()

        self.generate_group_stage_matches()

    def generate_matches(self):
        if self.stage == self.StageTypes.GROUP_STAGES:
            self.generate_group_stages()
        elif self.stage == self.StageTypes.ELIMINATION:
            self.generate_elimination_matches()
            

    def check_tournament_stage_transition(self):
        if self.stage == self.StageTypes.SIGNUPS_OPEN:
            if self.deadline is not None:
                if self.deadline < timezone.now():
                    self.stage = self.StageTypes.SIGNUPS_CLOSED
                    """if self.participants.count() < 16:
                        self.generate_elimination_matches()
                    else:
                        self.generate_group_stages()"""

        if self.stage == self.StageTypes.SIGNUPS_CLOSED:
            if self.date and self.date < timezone.now():
                if self.participants.count() < 16:
                    self.stage = self.StageTypes.ELIMINATION
                else:
                    self.stage = self.StageTypes.GROUP_STAGES
                
        elif self.stage == self.StageTypes.GROUP_STAGES:
            # If all group stage matches have been played, move to the next stage
            if not self.matches.filter(result=Match.MatchResultTypes.PENDING).exists():
                self.stage = self.StageTypes.ELIMINATION


        elif self.stage == self.StageTypes.ELIMINATION:
            # If all matches have been played, move to the next stage
            last_competing_group = Group.objects.filter(tournament=self).latest('elimination_stage')
            if last_competing_group.players.count() == 2 and self.matches.get(group=last_competing_group).result != Match.MatchResultTypes.PENDING: 
                self.stage = self.StageTypes.FINISHED
    
        self.save()

class TournamentParticipation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=False, related_name="participants")
    class Meta:
        unique_together = ("user", "tournament")


class Group(models.Model):
    name = models.CharField(max_length=100, blank=False)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=False, related_name="groups")
    players = models.ManyToManyField(User)

    elimination_stage = models.IntegerField(null=True)

    def get_group_results(self):
        group_results = {}
        for player in self.players.all():
            player_awards = 0
            for match in Match.objects.filter(
                    Q(tournament=self.tournament, white_player=player) | 
                    Q(tournament=self.tournament, black_player=player)):
                player_awards += match.get_match_award_for_user(player)
            group_results[player] = player_awards
        return group_results


class Match(models.Model):
    class MatchStageTypes(models.TextChoices):
        ELIMINATION = 'E'
        GROUP_STAGE = 'G'

    class MatchResultTypes(models.TextChoices):
        PENDING = 'P'
        WHITE_WIN = 'W'
        DRAW = 'D'
        BLACK_WIN = 'B'

    white_player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="+")
    black_player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="+")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=False, related_name="matches")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name="matches")
    result = models.CharField(max_length=1, choices=MatchResultTypes.choices, default=MatchResultTypes.PENDING)
    stage = models.CharField(max_length=1, choices=MatchStageTypes.choices, default=MatchStageTypes.ELIMINATION)

    MATCH_AWARDS = {
        "WIN": 1,
        "DRAW": 0.5,
        "LOSS": 0
    }

    def get_match_award_for_user(self, user):
        if user != self.white_player and user != self.black_player:
            raise ValueError("User not participant in match")

        if self.result == self.MatchResultTypes.PENDING:
            return 0

        if self.result == self.MatchResultTypes.DRAW:
            return self.MATCH_AWARDS["DRAW"]
        else:
            if user == self.white_player:
                if self.result == self.MatchResultTypes.WHITE_WIN:
                    return self.MATCH_AWARDS["WIN"]
                else:
                    return self.MATCH_AWARDS["LOSS"]
            else:
                if self.result == self.MatchResultTypes.BLACK_WIN:
                    return self.MATCH_AWARDS["WIN"]
                else:
                    return self.MATCH_AWARDS["LOSS"]


