'''Tournament Related Views'''
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime
from django.urls import reverse

from clubs.models import Club, Tournament, TournamentParticipation, Match, Membership
from clubs.forms import TournamentCreationForm

@login_required
def tournament_dashboard(request, tournament_id):
    """Allow user to view a tournament's dashboard, which contains tournament schedule, match results, tournament participants."""
    if request.method == 'POST':
        for e in request.POST:
            try:
                id = int(e)
                if Match.objects.filter(id=id).exists():
                    m = Match.objects.get(id=e)
                    m.result=request.POST[e]
                    m.save()
            except:
                pass
    # Get currently logged-in user
    user = request.user

    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except:
        tournament = None

    if tournament is not None:
        # If the specified tournament exists, get the data associated to this tournament

        tournament.check_tournament_stage_transition()

        club = tournament.club

        # Get the number of participants to the tournament
        participants_count = TournamentParticipation.objects.filter(tournament=tournament).count()
        participants_users = TournamentParticipation.objects.filter(tournament=tournament).values_list('user', flat=True)
        participants = Membership.objects.filter(user__in=participants_users, club=club)

        # Get all games scheduled for this tournament, as Match objects
        games = Match.objects.filter(tournament=tournament)

        status = {
            Tournament.StageTypes.SIGNUPS_OPEN: "Signups Open",
            Tournament.StageTypes.SIGNUPS_CLOSED: "Signups Closed",
            Tournament.StageTypes.ELIMINATION: "Elimination",
            Tournament.StageTypes.GROUP_STAGES: "Group Stages",
            Tournament.StageTypes.FINISHED: "Finished",
        }[tournament.stage]

        # Get the list of coorganizers of the tournament
        coorganizers = tournament.coorganizers.all()

        # Check if the logged-in user is already signed-up to the tournament
        try:
            TournamentParticipation.objects.get(tournament=tournament, user=user)
            is_signed_up = True
        except:
            is_signed_up = False

        return render(request, 'tournament_dashboard.html', {
            'club': club,
            'tournament': tournament,
            'user': user,
            'games': games,
            'participants': participants,
            'participants_count': participants_count,
            'is_signed_up': is_signed_up,
            'coorganizers': coorganizers,
            'status': status
        })

    else:
        return redirect('user_dashboard')


@login_required
def tournament_creation(request, club_id):
    """Allow clubs officers to create tournaments."""
    # Get the specified club
    club = Club.objects.get(id = club_id)
    if request.method == 'POST':
        form = TournamentCreationForm(data=request.POST)
        if form.is_valid():
            # The tournament-creation form is valid, the tournament is created and saved in the database
            t = form.save()
            redirect_url = reverse('tournament_dashboard', kwargs={'tournament_id':t.id})
            return redirect(redirect_url)
        else:
            if 'organizer' in form.errors:
                messages.add_message(request, messages.ERROR, form.errors['organizer'])
                return redirect('user_dashboard')
    else:
        form = TournamentCreationForm(initial = {'organizer': request.user, 'club': club})
    return render(request, 'new_tournament.html', {'form': form, 'club': club})

@login_required
def join_tournament(request, tournament_id):
    """Allow a club member to join a tournament."""
    # Get the specified Tournament object
    tournament = Tournament.objects.get(id=tournament_id)
    # Get currently logged-in user
    user = request.user
    # Attempt to join the tournament
    join_tournament_message = tournament.join_tournament(user)
    if join_tournament_message:
        messages.add_message(request, messages.ERROR, join_tournament_message)
    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return HttpResponse(status = 200)

@login_required
def leave_tournament(request, tournament_id):
    """Allow a tournament participant to leave the tournament."""
    # Get the specified Tournament object
    tournament = Tournament.objects.get(id=tournament_id)
    # Get currently logged-in user
    user = request.user
    # Attempt to leave the tournament
    leave_tournament_message = tournament.leave_tournament(user)
    if leave_tournament_message:
        messages.add_message(request, messages.ERROR, leave_tournament_message)
    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return HttpResponse(status = 200)

@login_required
def cancel_tournament(request, tournament_id):
    """Allow a tournament organizer to cancel the tournament."""
    # Get the specified Tournament object
    tournament = Tournament.objects.get(id=tournament_id)
    # Get currently logged-in user
    user = request.user
    # Attempt to cancel the tournament
    cancel_tournament_message = tournament.cancel_tournament(user)
    if cancel_tournament_message:
        messages.add_message(request, messages.ERROR, cancel_tournament_message)
    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return HttpResponse(status = 200)

@login_required
def generate_matches(request, tournament_id):
    """Generates matches for group and elimination stages"""
    # Get specified Tournament object
    tournament = Tournament.objects.get(id=tournament_id)
    # Get currently logged-in user
    user = request.user
    # Check if the logged-in user is an organizer for this tournament
    is_organizer = user in tournament.coorganizers.all() or tournament.organizer == user
    if is_organizer: # Generate matches only is the user is an organizer for this tournament
        message = tournament.generate_matches()
        messages.add_message(request, *message)
    else:
        messages.add_message(request, messages.ERROR, "You are not an organiser of this tournament")
    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return HttpResponse(status = 200)
