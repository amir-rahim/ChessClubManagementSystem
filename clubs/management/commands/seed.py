from django.core.management.base import BaseCommand, CommandError
from clubs.models import User, Club

class Command(BaseCommand):
    """The database seeder."""

    def handle(self, *args, **options):
        user = User.objects.create_user(username = "jkerman", password = "Password123.")
        user.username = "jkerman"
        user.name = "Jebediah Kerman"
        user.email = "jeb@example.org"
        user.save()

        user = User.objects.create_user(username = "bkerman", password = "Password123.")
        user.name = "Billie Kerman"
        user.email = "billie@example.org"
        user.save()
        
        Club.objects.create(name = "Kerbal Chess Club", owner = user)
