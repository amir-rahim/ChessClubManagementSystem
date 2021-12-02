from django.core.management.base import BaseCommand, CommandError
from clubs.models import User, Club, Membership

class Command(BaseCommand):
    """The database seeder."""

    def handle(self, *args, **options):
        user1 = User.objects.create_user(username = "jkerman", password = "Password123")
        user1.name = "Jebediah Kerman"
        user1.email = "jeb@example.org"
        user1.public_bio = "Welcome to my brand new profile!"
        user1.chess_experience = "B"
        user1.save()

        user2 = User.objects.create_user(username = "vkerman", password = "Password123")
        user2.name = "Valentina Kerman"
        user2.email = "val@example.org"
        user2.public_bio = "Welcome to my profile!"
        user2.chess_experience = "I"
        user2.save()

        user3 = User.objects.create_user(username = "bkerman", password = "Password123")
        user3.name = "Billie Kerman"
        user3.email = "billie@example.org"
        user3.public_bio = "Welcome to my profile!"
        user3.chess_experience = "A"
        user3.save()

        club1 = Club.objects.create(name = "Kerbal Chess Club", owner = user3)
        club1.location = "London, United Kingdom"
        club1.mission_statement = "We have the best players in the world!"
        club1.description = "We are a club to develop the best players in the world!"
        club1.save()

        membership1 = Membership.objects.create(user = user2, club = club1)
        membership1.personal_statement = "I want to join this club!"
        membership1.application_status = "A"
        membership1.user_type = "OF"
        membership1.save()

        membership2 = Membership.objects.create(user = user1, club = club1)
        membership2.personal_statement = "I really like this club!"
        membership2.application_status = "A"
        membership2.user_type = "MB"
        membership2.save()
