from django.core.management.base import BaseCommand, CommandError
from clubs.models import User, Club

class Command(BaseCommand):
    """The database unseeder."""

    def handle(self, *args, **options):
        User.objects.get(username="Jebediah Kerman").delete()
        Club.objects.get(name="Kerbal Chess Club").delete()
