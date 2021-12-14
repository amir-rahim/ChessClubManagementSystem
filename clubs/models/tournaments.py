from django.db import models
from django.utils import timezone
from django.db.models import Q
from .users import User
from .clubs import Club, Membership
import random
from datetime import datetime
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
    coorganizers = models.ManyToManyField(User, related_name="coorganizers", blank=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=False)
    capacity = models.IntegerField(null=True)
    deadline = models.DateTimeField(null=True)
    stage = models.CharField(max_length=1, choices=StageTypes.choices, default=StageTypes.SIGNUPS_OPEN)

    def competing_players(self):
        if not Group.objects.filter(tournament=self).exists():
            return self.participants.values_list('user', flat=True)

        latest_competing_group = Group.objects.filter(tournament=self).latest('phase')
        last_competing_groups = Group.objects.filter(tournament=self, phase=latest_competing_group.phase)
        competing_players = []
        for last_competing_group in last_competing_groups:
            for player in last_competing_group.players.all():
                competing_players.append(player)


        return competing_players

    @property
    def group_phase(self):
        participants = self.competing_players()
        return 1 if (len(participants) <= 32) else 0

    @property
    def group_size(self):
        return 4 if self.group_phase == 1 else 6


    def generate_elimination_matches(self):
        # TODO: Check all matches completed

        # Generate groups from each stage
        group = None
        rescheduled_matches = []

        # If last stage was not elimination
        if not self.groups.filter(stage=Group.GroupStageTypes.ELIMINATION).exists():
            # If not first stage
            if Group.objects.filter(tournament=self).exists():
                competing_players = []
                last_competing_group = Group.objects.filter(tournament=self).latest('phase')
                last_competing_groups = Group.objects.filter(tournament=self, phase=last_competing_group.phase)
                for group in last_competing_groups:
                    group_results = group.get_group_results()

                    for group_result in sorted(group_results, key=group_results.get, reverse=True)[:2]:
                        competing_players.append(group_result)

                group = Group(tournament=self, name='Elimination 1', phase=0, stage=Group.GroupStageTypes.ELIMINATION)
                group.save()
                for competing_player in competing_players:
                    group.players.add(competing_player)

            # If first stage (with no group stages preceeding)
            else:
                competing_players = self.competing_players()
                group = Group(tournament=self, name='Elimination 1', phase=0, stage=Group.GroupStageTypes.ELIMINATION)
                group.save()
                for competing_player in competing_players:
                    group.players.add(competing_player)
        else:
            last_competing_group = Group.objects.filter(tournament=self).latest('phase')
            last_competing_players = self.competing_players()
            last_matches = self.matches.filter(group=last_competing_group)

            players_within_matches = []
            for last_match in last_matches:
                players_within_matches.append(last_match.white_player)
                players_within_matches.append(last_match.black_player)

            competing_players = []

            # Add bye player to competitors based on player not within matches
            for last_competing_player in last_competing_players:
                if not last_competing_player in players_within_matches:
                    competing_players.append(last_competing_player)

            for match in self.matches.filter(group=last_competing_group):
                if match.result == Match.MatchResultTypes.WHITE_WIN:
                    competing_players.append(match.white_player)
                elif match.result == Match.MatchResultTypes.BLACK_WIN:
                    competing_players.append(match.black_player)

                # TODO: Change functionality to reschedule match
                elif match.result == Match.MatchResultTypes.DRAW:
                    rescheduled_matches.append(match)

            if not rescheduled_matches:
                group_index = last_competing_group.phase + 1
                group = Group(tournament=self, name=f'Elimination {group_index+1}', stage=Group.GroupStageTypes.ELIMINATION, phase=group_index)
                group.save()
                for competing_player in competing_players:
                    group.players.add(competing_player)

        if rescheduled_matches:
            for match in rescheduled_matches:
                match = Match(white_player=match.white_player,
                              black_player=match.black_player,
                              tournament=self,
                              group=last_competing_group)

        else:
            group_players = list(group.players.all())

            if len(group_players) % 2 != 0:
                bye_player = group_players[-1]
                group_players.remove(bye_player)

            it = iter(group_players)
            players_of_matches = zip(it,it)

            for players_of_match in players_of_matches:
                match = Match(white_player=players_of_match[0],
                              black_player=players_of_match[1],
                              tournament=self,
                              group=group)
                match.save()


    def generate_group_stage_matches(self, groups):
        # Generate group stage matches
        for group in groups:
            # TODO: Generate matches for each group
            for white_player, black_player in itertools.combinations(group.players.all(), 2):
                match = Match(tournament=self, white_player=white_player, black_player=black_player, group=group)
                match.save()

    def generate_group_stages(self):
        group_phase = 1 if self.participants.count() <= 32 else 0
        # Generate group stages
        if not self.groups.filter(stage=Group.GroupStageTypes.GROUP_STAGE).exists():
            competing_players = self.competing_players()
        else:
            group_phase = 1
            latest_competing_group = Group.objects.filter(tournament=self).latest('phase')
            last_competing_groups = Group.objects.filter(tournament=self, phase=latest_competing_group.phase)

            competing_players = []
            for group in last_competing_groups:
                group_results = group.get_group_results()

                for group_result in sorted(group_results, key=group_results.get, reverse=True)[:2]:
                    competing_players.append(group_result)


        group_size = 4 if group_phase == 1 else 6
        group_count = len(competing_players) // self.group_size

        groups = []
        for i in range(group_count):
            group_letter = chr(ord('@')+(i+1))
            group = Group(tournament=self, name=f'Group {group_letter}', stage=Group.GroupStageTypes.GROUP_STAGE, phase=group_phase)
            group.save()

            for j in range(group_size):
                group.players.add(competing_players[i * group_size + j])

            group.save()
            groups.append(group)

        self.generate_group_stage_matches(groups)

    def generate_matches(self):
        if not self.matches.filter(result=Match.MatchResultTypes.PENDING).exists():
            if self.stage == self.StageTypes.GROUP_STAGES:
                self.generate_group_stages()
            elif self.stage == self.StageTypes.ELIMINATION:
                self.generate_elimination_matches()
            return True
        else:
            return False


    def check_tournament_stage_transition(self):
        if self.stage == self.StageTypes.SIGNUPS_OPEN:
            if self.deadline is not None:
                if self.deadline < timezone.now():
                    self.stage = self.StageTypes.SIGNUPS_CLOSED

        if self.stage == self.StageTypes.SIGNUPS_CLOSED:
            if self.date and self.date < timezone.now():
                if self.participants.count() <= 16:
                    self.stage = self.StageTypes.ELIMINATION
                else:
                    self.stage = self.StageTypes.GROUP_STAGES

        elif self.stage == self.StageTypes.GROUP_STAGES:
            # If all group stage matches have been played
            if not self.matches.filter(result=Match.MatchResultTypes.PENDING).exists():
                if len(self.competing_players()) <= 33:
                    self.stage = self.StageTypes.ELIMINATION


        elif self.stage == self.StageTypes.ELIMINATION:
            # If all matches have been played, move to the next stage
            last_competing_group = Group.objects.filter(tournament=self).latest('phase')
            if last_competing_group.players.count() == 2 and self.matches.get(group=last_competing_group).result != Match.MatchResultTypes.PENDING:
                self.stage = self.StageTypes.FINISHED

        self.save()

    def join_tournament(self, user):
        current_datetime = timezone.make_aware(datetime.now(), timezone.utc)
        if current_datetime < self.deadline:
            try:
                membership = Membership.objects.get(user=user, club=self.club)
                if (Membership.UserTypes.MEMBER in membership.get_user_types()):
                    if user != self.organizer:
                        try:
                            current_participants_count = TournamentParticipation.objects.filter(tournament=self).count()
                        except:
                            current_participants_count = 0
                        if (current_participants_count < self.capacity):
                            new_participation = TournamentParticipation(user=user, tournament=self)
                            try:
                                new_participation.full_clean()
                                new_participation.save()
                                return ""
                            except:
                                return "You are already signed up to this tournament."
                        else:
                            return "This tournament has reached max capacity, you cannot join it."
                    else:
                        return "You are organizing this tournament, you cannot join it."
                else:
                    return "You are not a member of this club, you cannot join the tournament."
            except:
                return "You are not a member of this club, you cannot join the tournament."
        else:
            return "You cannot join the tournament once the sign-up deadline has passed."

    def leave_tournament(self, user):
        current_datetime = timezone.make_aware(datetime.now(), timezone.utc)
        if current_datetime < self.deadline:
            try:
                tournament_participation = TournamentParticipation.objects.get(user=user, tournament=self)
                if tournament_participation:
                    tournament_participation.delete()
                    return ""
                else:
                    return "You are not signed-up for this tournament."
            except:
                return "You are not signed-up for this tournament."
        else:
            return "You cannot leave the tournament once the sign-up deadline has passed."

    def cancel_tournament(self, user):
        if user == self.organizer:
            if (self.stage == 'S' or self.stage == 'C'):
                self.delete()
                return ""
            else:
                return "This tournament has already started."
        else:
            return "You are not an organizer for this tournament."


class TournamentParticipation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=False, related_name="participants")
    class Meta:
        unique_together = ("user", "tournament")


class Group(models.Model):
    class GroupStageTypes(models.TextChoices):
        ELIMINATION = 'E'
        GROUP_STAGE = 'G'

    name = models.CharField(max_length=100, blank=False)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=False, related_name="groups")
    players = models.ManyToManyField(User)

    stage = models.CharField(max_length=1, choices=GroupStageTypes.choices, default=GroupStageTypes.ELIMINATION)
    phase = models.IntegerField()

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
