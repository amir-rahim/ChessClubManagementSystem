from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import make_aware

from clubs.models.users import User
from clubs.models.clubs import Club, Membership
from clubs.models.tournaments import Tournament, TournamentParticipation, Match, Group

import pytz
from faker import Faker
from random import randint, random

from datetime import datetime, timezone

class Command(BaseCommand):
    """The database seeder."""

    USER_COUNT = 500
    CLUB_COUNT = 20
    TOURNAMENT_COUNT = 5
    MEMBER_CHANCE = 0.2
    APPROVE_CHANCE = 0.9
    OFFICER_CHANCE = 0.1
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_default_users()
        self.create_users()
        self.users = User.objects.exclude(is_superuser=True)
        self.create_clubs()
        self.clubs = Club.objects.all()
        self.create_default_memberships()
        self.make_memberships()
        self.memberships = Membership.objects.all()
        self.create_tournaments()
        self.tournaments = Tournament.objects.all()
        self.participants = TournamentParticipation.objects.all()

    def create_default_users(self):
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

        print("Default Users seeding complete.      ")

        club1 = Club.objects.create(name = "Kerbal Chess Club", owner = user3)
        club1.location = "London, United Kingdom"
        club1.mission_statement = "We have the best players in the world!"
        club1.description = "We are a club to develop the best players in the world!"
        club1.save()

        print("Default Club seeding complete.      ")


    def create_users(self):
        user_count = 3
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            try:
                self.create_user_profile()
            except:
                continue
            user_count = user_count + 1
        print("User seeding complete.      ")

    def create_user_profile(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        name = first_name + " " + last_name
        email = self.create_email(first_name, last_name)
        username = self.create_username(first_name, last_name)
        public_bio = self.faker.text(max_nb_chars=250)
        chess_experience = 'B'
        random_chess_experience = random()

        if random_chess_experience <= 0.20:
            chess_experience = 'B'
        elif random_chess_experience <= 0.40:
            chess_experience = 'I'
        elif random_chess_experience <= 0.60:
            chess_experience = 'A'
        elif random_chess_experience <= 0.80:
            chess_experience = 'M'
        else:
            chess_experience = 'G'

        user_create = User.objects.create_user(username=username, 
                                               name=name,
                                               password=Command.DEFAULT_PASSWORD,
                                               email=email,
                                               public_bio=public_bio,
                                               chess_experience=chess_experience)


        user_create.save()

    def create_email(self, first_name, last_name):
        return first_name + '.' + last_name + '@example.org'

    def create_username(self, first_name, last_name):
        return first_name.lower() + last_name.lower()

    def get_random_user(self):
        index = randint(0,self.users.count()-1)
        return self.users[index]

    def create_clubs(self):
        club_count = 2
        while club_count < self.CLUB_COUNT:
            print(f"Seeding club {club_count}/{self.CLUB_COUNT}", end='\r')
            try:
                self.create_club()
            except:
                continue
            club_count = club_count + 1
        print("Club seeding complete.      ")

    def create_club(self):
        name = self.faker.company()
        owner = self.get_random_user()
        location = self.faker.city()
        mission_statement = self.faker.catch_phrase()
        description = self.faker.text(max_nb_chars=500)

        club = Club.objects.create(
            name=name,
            owner=owner,
            location=location,
            mission_statement=mission_statement,
            description=description
        )

        club.save()

    def make_memberships(self):
        count = 1
        for user in self.users:
            for club in self.clubs:
                if not Membership.objects.filter(club=club, user=user).exists():
                    if random() < self.MEMBER_CHANCE:

                        if random() < self.APPROVE_CHANCE:
                            application_status = 'A'

                            if random() < self.OFFICER_CHANCE:
                                user_type = 'OF'
                            else:
                                user_type = 'MB'
                        else:
                            application_status = 'P'
                            user_type = 'NM'
                                

                        print(f"Seeding memberships, Count:{count}", end='\r')

                        personal_statement = self.faker.text(max_nb_chars=500)

                        membership = Membership.objects.create(
                            user=user,
                            club=club,
                            personal_statement=personal_statement,
                            application_status=application_status,
                            user_type=user_type
                        )
                        
                        membership.save()
                        
                        count += 1

        print("Memberships seeding complete.      ")

    def create_default_memberships(self):

        vkerman = self.users.get(name="Valentina Kerman")
        jkerman = self.users.get(name="Jebediah Kerman")
        kerbal = self.clubs.get(name="Kerbal Chess Club")

        member_check1 = Membership.objects.create(
                user = vkerman, 
                club = kerbal,
                personal_statement = "I want to join this club!",
                application_status = "A",
                user_type = "OF")
        member_check2 = Membership.objects.create(
                user = jkerman, 
                club = kerbal,
                personal_statement = "I really like this club!",
                application_status = "A",
                user_type = "MB")

        member_check1.save()
        member_check2.save()

        print("Default Memberships seeding complete.      ")

    def create_tournaments(self):
        for club in self.clubs:
            tournament_count = 1
            
            potential_organizers = self.memberships.filter(club=club, user_type=Membership.UserTypes.OFFICER).order_by('?')

            while tournament_count < self.TOURNAMENT_COUNT:
                
                name = self.faker.name()
                deadline = make_aware(self.faker.date_time_between(end_date=datetime(2020, 8, 31, 13, 50, 6)))
                date = make_aware(self.faker.date_time_between(start_date=datetime(2020, 8, 31, 13, 50, 6)))

                organizer = potential_organizers.first().user

                tournament = Tournament.objects.create(name=name,
                    description=self.faker.text(max_nb_chars=1000),
                    date=date,
                    organizer=organizer,
                    club=club,
                    capacity=randint(0,96),
                    deadline=deadline,
                    stage=Tournament.StageTypes.SIGNUPS_OPEN)
                
                tournament.save()
                
                self.create_participants(tournament)
                
                tournament_count += 1
                
        print("Tournament seeding complete.      ")

    def create_participants(self, tournament):
        max = tournament.capacity
        club = tournament.club
        
        members = Membership.objects.filter(club=club).exclude(user=tournament.organizer).order_by('?')
        current_count = 0
        
        if max > members.count():
            user_count = randint(0, members.count())
        else:
            user_count = randint(0, max)
        
        for current_count in range(user_count):

            participant = TournamentParticipation.objects.get_or_create(
                user=members[current_count].user, 
                tournament=tournament
            )

