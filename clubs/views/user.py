'''User Related Views'''
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from clubs.models import Membership, Tournament, TournamentParticipation, Match, EloRating, User

@login_required
def user_dashboard(request):
    """Show user dashbaord."""
    data = {'user': request.user}
    return render(request, 'user_dashboard.html', data)

@login_required
def user_profile(request, user_id = None, membership_id = None):
    """Show user profile."""
    if user_id is not None and membership_id is not None:
        try:
            # Get the Membership & User object specified by url parameters
            membership = Membership.objects.get(id=membership_id)
            user = User.objects.get(id=user_id)
        except (Membership.DoesNotExist, User.DoesNotExist) as e:
            messages.error(request, 'Membership does not exist')
            return redirect('user_dashboard')

        # Get Membership object of current user
        request_membership = Membership.objects.filter(user=request.user, club=membership.club).first()

        if request_membership is None:
            messages.error(request, 'You do not have permission to view this user profile.')
            return redirect('user_dashboard')
        data = {'user' : user, 'membership' : request_membership}
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
