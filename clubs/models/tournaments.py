from django.db import models
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'club'], name='unique_tournament_club'),
        ]

    """Attributes of a tournament"""
    name = models.CharField(max_length=100, blank=False, unique=False)
    description = models.CharField(max_length=1000, blank=False)
    date = models.DateTimeField(blank=True, null=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    coorganizers = models.ManyToManyField(User, related_name="coorganizers", blank=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=False)
    capacity = models.IntegerField(null=True)
    deadline = models.DateTimeField(null=True)
    stage = models.CharField(max_length=1, choices=StageTypes.choices, default=StageTypes.SIGNUPS_OPEN)

    def competing_players(self):
        """Returns players that are competing"""
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
        """Creates matches for elimination matches"""
        # Generate groups from each stage
        match_count = 0

        group = None
        rescheduled_matches = []
        last_competing_groups = None

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

                group = Group(tournament=self, name='Elimination 1', phase=last_competing_group.phase+1, stage=Group.GroupStageTypes.ELIMINATION)
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
                else:
                    # If there doesn't exist a match between the players in the same round which has a result
                    if not Match.objects.filter(white_player=match.white_player, black_player=match.black_player, tournament=self, group=last_competing_group).filter(Q(_result=Match.MatchResultTypes.WHITE_WIN) | Q(_result=Match.MatchResultTypes.BLACK_WIN)).exists():
                        rescheduled_matches.append(match)

            if not rescheduled_matches:
                group_index = last_competing_group.phase + 1
                group = Group(tournament=self, name=f'Elimination {group_index}', stage=Group.GroupStageTypes.ELIMINATION, phase=group_index)
                group.save()
                for competing_player in competing_players:
                    group.players.add(competing_player)

        if rescheduled_matches:
            for match in rescheduled_matches:
                match = Match(white_player=match.white_player,
                              black_player=match.black_player,
                              tournament=self,
                              group=last_competing_group)
                match.save()
                match_count += 1
            return (messages.SUCCESS, f'{match_count} matches rescheduled.')
        else:
            group_players = list(group.players.all())

            if len(group_players) % 2 != 0:
                bye_player = group_players[-1]
                group_players.remove(bye_player)

            # Order group players to ensure players of the same group
            # are matched against each other at the latest opportunity
            if last_competing_groups:
                ordered_group_players = []
                group_players_id = [player.id for player in group_players]
                for last_competing_group in last_competing_groups:
                    ordered_group_players.append(last_competing_group.players.filter(id__in=group_players_id)[0])

                for last_competing_group in last_competing_groups:
                    ordered_group_players.append(last_competing_group.players.filter(id__in=group_players_id)[1])
            else:
                ordered_group_players = group_players


            it = iter(ordered_group_players)
            players_of_matches = zip(it,it)

            for players_of_match in players_of_matches:
                match = Match(white_player=players_of_match[0],
                              black_player=players_of_match[1],
                              tournament=self,
                              group=group)
                match.save()
                match_count += 1
            return (messages.SUCCESS, f'{match_count} elimination stage matches generated.')



    def generate_group_stage_matches(self, groups):
        # Generate group stage matches
        match_count = 0
        for group in groups:
            for white_player, black_player in itertools.combinations(group.players.all(), 2):
                match = Match(tournament=self, white_player=white_player, black_player=black_player, group=group)
                match.save()
                match_count += 1
        return (messages.SUCCESS, f'{match_count} group stage matches generated.')

    def generate_group_stages(self):
        """Creates matches for the group stages"""
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
        group_count = len(competing_players) // group_size

        groups = []
        for i in range(group_count):
            group_letter = chr(ord('@')+(i+1))
            group = Group(tournament=self, name=f'Group {group_letter}', stage=Group.GroupStageTypes.GROUP_STAGE, phase=group_phase)
            group.save()

            for j in range(group_size):
                group.players.add(competing_players[i * group_size + j])

            group.save()
            groups.append(group)

        return self.generate_group_stage_matches(groups)

    def generate_matches(self):
        """Generates matches for group and elimination stages"""
        if not self.matches.filter(_result=Match.MatchResultTypes.PENDING).exists():
            if self.stage == self.StageTypes.GROUP_STAGES:
                return self.generate_group_stages()
            elif self.stage == self.StageTypes.ELIMINATION:
                return self.generate_elimination_matches()
            else:
                return (messages.ERROR, 'Matches can only be generated in '
                                        'group stages or elimination stages.')
        else:
            return (messages.WARNING, 'Matches already generated.')


    def check_tournament_stage_transition(self):
        """Checks whether previous stages of the tournament have been completed and moves to the next stage"""
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
            if not self.matches.filter(_result=Match.MatchResultTypes.PENDING).exists():
                if len(self.competing_players()) <= 32:
                    self.stage = self.StageTypes.ELIMINATION


        elif self.stage == self.StageTypes.ELIMINATION:
            # If all matches have been played, move to the next stage
            if Group.objects.filter(tournament=self).exists():
                last_competing_group = Group.objects.filter(tournament=self).latest('phase')
                if last_competing_group.players.count() == 2 and self.matches.get(group=last_competing_group).result != Match.MatchResultTypes.PENDING:
                    self.stage = self.StageTypes.FINISHED

        self.save()

    def join_tournament(self, user):
        current_datetime = timezone.make_aware(datetime.now(), timezone.utc)
        # The sign-up deadline must not have passed to be able to join the tournament
        if current_datetime < self.deadline:
            # The user must be member of the club to join the tournament
            try:
                membership = Membership.objects.get(user=user, club=self.club)
                # The user must not be one of the tournament's organizers to be able to join the tournament
                if (Membership.UserTypes.MEMBER in membership.get_user_types()):
                    if user != self.organizer and user not in self.coorganizers.all():
                        current_participants_count = TournamentParticipation.objects.filter(tournament=self).count()

                        # The user cannot join the tournament if it is already full
                        if (current_participants_count < self.capacity):
                            # The user is added to the tournament with a new TournamentParticipation object
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
        # The sign-up deadline must not have passed to be able to leave the tournament
        if current_datetime < self.deadline:
            try:
                tournament_participation = TournamentParticipation.objects.get(user=user, tournament=self)
                if tournament_participation:
                    # We remove the user from the tournament by deleting the corresponding TournamentParticipation object
                    tournament_participation.delete()
                    return ""
                else:
                    return "You are not signed-up for this tournament."
            except:
                return "You are not signed-up for this tournament."
        else:
            return "You cannot leave the tournament once the sign-up deadline has passed."

    def cancel_tournament(self, user):
        # The user must be of the tournament's organizers to be able to cancel the tournament
        if user == self.organizer or user in self.coorganizers.all():
            # The tournament must not already have started, to be able to be cancelled
            if (self.stage == 'S' or self.stage == 'C'):
                # We cancel the tournament by deleting the corresponding Tournament object ; all associated objects are also deleted via CASCADE
                self.delete()
                return ""
            else:
                return "This tournament has already started."
        else:
            return "You are not an organizer for this tournament."


class TournamentParticipation(models.Model):
    """Store users participated in tournaments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=False, related_name="participants")
    class Meta:
        unique_together = ("user", "tournament")


class Group(models.Model):
    class GroupStageTypes(models.TextChoices):
        ELIMINATION = 'E'
        GROUP_STAGE = 'G'
    """Attributes off groups"""
    name = models.CharField(max_length=100, blank=False)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=False, related_name="groups")
    players = models.ManyToManyField(User)

    stage = models.CharField(max_length=1, choices=GroupStageTypes.choices, default=GroupStageTypes.ELIMINATION)
    phase = models.IntegerField()

    def get_group_results(self):
        """returns the restults of the players in the groups"""
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
    """Attributes of the matches"""
    white_player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="+")
    black_player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="+")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=False, related_name="matches")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name="matches")
    _result = models.CharField(max_length=1, choices=MatchResultTypes.choices, default=MatchResultTypes.PENDING)

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        """Sets the results of matches"""
        self._result = value
        self.result_date = timezone.now()

    result_date = models.DateTimeField(null=True, blank=True)

    MATCH_AWARDS = {
        "WIN": 1,
        "DRAW": 0.5,
        "LOSS": 0
    }

    def get_match_award_for_user(self, user):
        """Returns the outcome of the matches"""
        if user != self.white_player and user != self.black_player:
            raise ValueError("User not participant in match")

        if self.result == self.MatchResultTypes.PENDING:
            #return 0
            raise ValueError("Match result not yet set")

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

class EloRating():
    @staticmethod
    def calculate_new_elo_rating(rating_a, player_a, rating_b, player_b, match):
        expected_score_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
        expected_score_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))

        new_rating_a = rating_a + 32 * (match.get_match_award_for_user(player_a) - expected_score_a)
        new_rating_b = rating_b + 32 * (match.get_match_award_for_user(player_b) - expected_score_b)

        return new_rating_a, new_rating_b

    @staticmethod
    def get_ratings(membership, date = None):
        if not date:
            date = timezone.now()

        matches = Match.objects.filter(
            Q(white_player = membership.user) | Q(black_player = membership.user)
        ).filter(
            result_date__lt=date
        ).order_by('result_date')

        current_rating = 1000
        ratings = [(1000,None)]
        for match in matches:
            if match.white_player == membership.user:
                player_b = match.black_player
            else:
                player_b = match.white_player

            player_b_membership = Membership.objects.get(user = player_b, club = membership.club)
            rating_b = EloRating.get_ratings(player_b_membership, match.result_date)[-1][0]

            current_rating = EloRating.calculate_new_elo_rating(current_rating, membership.user, rating_b, player_b, match)[0]
            ratings.append((current_rating, match.result_date))

        if current_rating < membership.lowest_elo_rating:
            membership.lowest_elo_rating = current_rating
            membership.save()
        elif current_rating > membership.highest_elo_rating:
            membership.highest_elo_rating = current_rating
            membership.save()

        return ratings
