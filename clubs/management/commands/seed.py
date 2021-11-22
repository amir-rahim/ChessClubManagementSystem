from django.core.management.base import BaseCommand, CommandError
from clubs.models import User, Club, Membership

class Command(BaseCommand):
    """The database seeder."""

    def handle(self, *args, **options):
        user1 = User.objects.create_user(username = "jkerman", password = "Password123.")
        user1.username = "jkerman"
        user1.name = "Jebediah Kerman"
        user1.email = "jeb@example.org"
        user1.save()

        user2 = User.objects.create_user(username = "bkerman", password = "Password123.")
        user2.name = "Billie Kerman"
        user2.email = "billie@example.org"
        user2.save()

        club1 = Club.objects.create(name = "Kerbal Chess Club", owner = user2)
        club1.save()

        #Membership.objects.create(user = user2, club = club1)
