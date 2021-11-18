from django.core.management.base import BaseCommand, CommandError
from clubs.models import User, Club

class Command(BaseCommand):
    """The database unseeder."""

    def handle(self, *args, **options):
        user1 = User.objects.get(username="bkerman")
        Club.objects.get(name="Kerbal Chess Club", owner=user1).delete()
        User.objects.get(username="jkerman").delete()
        User.objects.get(username="bkerman").delete()
