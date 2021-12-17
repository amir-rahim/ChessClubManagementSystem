'''User Related Views'''
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from clubs.models import Membership, Tournament, TournamentParticipation, Match, EloRating

@login_required
def user_dashboard(request):
    """Show user dashbaord."""
    data = {'user': request.user}
    return render(request, 'user_dashboard.html', data)

@login_required
def user_profile(request):
    """Show user profile."""
    if request.method == 'POST':
        # Get the specified Membership object, and extract the corresponsing User object
        membership = Membership.objects.get(pk = request.POST['membership'])
        data = {'user' : membership.user, 'membership' : membership}
    else :
        data = {'user': request.user, "my_profile" : True}
    return render(request, 'user_profile.html', data)


@login_required
def member_profile(request, membership_id):
    """Information of a member when a member profile is viewed. Redirects to user dashboard if there is no club."""
    # Get currently logged-in user
    user = request.user
    # Get the specified Membership object
    try:
        membership = Membership.objects.get(id=membership_id)
    except:
        membership = None

    if membership is not None:
        # If the specified Membership object exists, get the data related to the membership
        club = membership.club

        if not Membership.objects.filter(user=user, club=club).exists():
            messages.add_message(request, messages.ERROR, "You are not a member of this club.")
            return redirect('user_dashboard')

        # Get the tournament data associated with this member
        matches = list(Match.objects.filter(Q(tournament__club=club) & Q(white_player=membership.user) | Q(black_player=membership.user)))
        tournament_ids = TournamentParticipation.objects.filter(user=membership.user).values_list('tournament', flat=True).distinct()
        tournaments = list(Tournament.objects.filter(id__in=tournament_ids))

        # Get the member's ELO Ratings
        elo_ratings = EloRating.get_ratings(membership)
        match_statistics = [
            sum((match.result == Match.MatchResultTypes.WHITE_WIN and match.white_player == membership.user) or (match.result == Match.MatchResultTypes.BLACK_WIN and match.black_player == membership.user) for match in matches),
            sum((match.result == Match.MatchResultTypes.BLACK_WIN and match.white_player == membership.user) or (match.result == Match.MatchResultTypes.WHITE_WIN and match.black_player == membership.user) for match in matches),
            sum((match.result == Match.MatchResultTypes.DRAW and match.white_player == membership.user) or (match.result == Match.MatchResultTypes.DRAW and match.black_player == membership.user) for match in matches)
        ]

        return render(request, 'member_profile.html', {
            'club': club,
            'membership': membership,
            'user': membership.user,
            'matches': matches,
            'match_statistics': match_statistics,
            'tournaments': tournaments,
            'elo_ratings': elo_ratings
        })

    else:
        messages.add_message(request, messages.ERROR, "Member not found.")
        return redirect('user_dashboard')
