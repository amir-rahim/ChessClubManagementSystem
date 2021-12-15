from django.core.management.base import BaseCommand, CommandError
from clubs.models.users import User
from clubs.models.clubs import Club, Membership
from clubs.models.tournaments import Tournament, TournamentParticipation, Match, Group

class Command(BaseCommand):
    """The database unseeder."""

    help = 'Unseeds the database with sample data'

    def handle(self, *args, **options):
        User.objects.filter(is_superuser=False).delete()
        Club.objects.all().delete()
        Membership.objects.all().delete()
        Tournament.objects.all().delete()
        TournamentParticipation.objects.all().delete()
        Match.objects.all().delete()
        Group.objects.all().delete()
