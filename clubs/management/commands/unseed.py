from django.core.management.base import BaseCommand, CommandError
from clubs.models import User, Club, Membership

class Command(BaseCommand):
    """The database unseeder."""

    def handle(self, *args, **options):
        user2 = User.objects.get(username="bkerman")
        club1 = Club.objects.get(name = "Kerbal Chess Club", owner = user2)


        Membership.objects.get(user = user2, club = club1).delete()

        Club.objects.get(name="Kerbal Chess Club", owner=user2).delete()

        User.objects.get(username="jkerman").delete()
        User.objects.get(username="bkerman").delete()
