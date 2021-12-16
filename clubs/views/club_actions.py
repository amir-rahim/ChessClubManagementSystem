'''Actions in Clubs Related Views'''
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from clubs.models import Membership, Club, User

@login_required
def promote_member(request, club_id, user_id):
    current_user = request.user
    try:
        current_user_membership = Membership.objects.get(user=current_user, club=club_id)
        if Membership.UserTypes.OWNER in current_user_membership.get_user_types():
            membership_to_promote = Membership.objects.get(club = club_id, user=user_id)
            membership_to_promote.promote_to_officer()
        else:
            messages.add_message(request, messages.ERROR, "You are not allowed to promote users.")
    except:
        messages.add_message(request, messages.ERROR, "Error promoting user.")

    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return HttpResponse(status = 200)

@login_required
def demote_member(request, club_id, user_id):
    current_user = request.user
    try:
        current_user_membership = Membership.objects.get(user=current_user, club=club_id)
        if Membership.UserTypes.OWNER in current_user_membership.get_user_types():
            membership_to_demote = Membership.objects.get(club = club_id, user=user_id)
            membership_to_demote.demote_to_member()
        else:
            messages.add_message(request, messages.ERROR, "You are not allowed to demote users.")
    except:
        messages.add_message(request, messages.ERROR, "Error demoting user.")

    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return HttpResponse(status = 200)

@login_required
def kick_member(request, club_id, user_id):
    current_user = User.objects.get(id=user_id)
    try:
        current_user_membership = Membership.objects.get(user=current_user, club=club_id)
        if Membership.UserTypes.OWNER or Membership.UserTypes.OFFICER in current_user_membership.get_user_types():
            membership_to_kick = Membership.objects.get(club = club_id, user=user_id)
            membership_to_kick.kick_member()
        else:
            messages.add_message(request, messages.ERROR, "You are not allowed to kick users.")
    except:
        messages.add_message(request, messages.ERROR, "Error kicking user.")

    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return HttpResponse(status = 200)

@login_required
def transfer_ownership(request, club_id, user_id):
    current_user = request.user
    try:
        current_user_membership = Membership.objects.get(user=current_user, club=club_id)
        if Membership.UserTypes.OWNER in current_user_membership.get_user_types():
            user_to_transfer = User.objects.get(id=user_id)
            current_user_membership.transfer_ownership(user_to_transfer)
        else:
            messages.add_message(request, messages.ERROR, "You are not allowed to transfer ownership.")
    except Exception as e:
        messages.add_message(request, messages.ERROR, str(e))

    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return HttpResponse(status = 200)

@login_required
def leave_club(request, club_id):
    current_user = request.user
    try:
        club = Club.objects.get(id=club_id)
        current_user_membership = Membership.objects.get(user=current_user, club=club_id)
        if current_user_membership.leave():
            messages.add_message(request, messages.SUCCESS, f"Successfully left {club.name}.")
        else:
            raise Exception("You are not allowed to leave this club.")
    except Exception as e:
        messages.add_message(request, messages.ERROR, "Error leaving club: " + str(e))

        if request.GET.get('previous'):
            return redirect(request.GET.get('previous'))
        else:
            return HttpResponse(status = 500)

    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return HttpResponse(status = 200)

@login_required
def accept_membership(request, membership_id):
    membership = Membership.objects.get(id=membership_id)
    membership.approve_membership()
    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return HttpResponse(status = 200)

@login_required
def reject_membership(request, membership_id):
    membership = Membership.objects.get(id=membership_id)
    membership.deny_membership()
    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return HttpResponse(status = 200)