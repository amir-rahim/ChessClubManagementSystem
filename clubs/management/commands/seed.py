from django.core.management.base import BaseCommand, CommandError
from clubs.models import User, Club

class Command(BaseCommand):
    """The database seeder."""

    def handle(self, *args, **options):
        user = User.objects.create_user("JKerman","Password123")
        user.name = "Jebediah Kerman"
        user.email = "jebediah.kerman@gmail.com"
        user.save()
        Club.objects.create(name="Kerbal Chess Club")
