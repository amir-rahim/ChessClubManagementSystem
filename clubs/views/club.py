'''Club Related Views'''
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse

from clubs.models import Membership, Club, Tournament
from clubs.forms import ClubCreationForm, EditClubDetailsForm

@login_required
def club_dashboard(request, club_id):
    user = request.user
    membership = None

    try:
        club = Club.objects.get(id=club_id)
    except:
        club = None

    if club is not None:
        membership = Membership.objects.filter(user=user, club=club).first()
        members = Membership.objects.filter(club=club).exclude(user_type = Membership.UserTypes.NON_MEMBER)
        officers = Membership.objects.filter(club=club).filter(user_type = Membership.UserTypes.OFFICER)
        applications = Membership.objects.filter(club=club, application_status='P')
        tournaments = Tournament.objects.filter(club=club)

        return render(request, 'club_dashboard.html', {
            'club': club,
            'membership': membership,
            'members': members,
            'officers': officers,
            'applications': applications,
            'user': user,
            'tournaments': tournaments
        })
    else:
        messages.add_message(request, messages.ERROR, "Club does not exist.")
        return redirect('user_dashboard')

@login_required
def club_creation(request):
    if request.method == 'POST':
        form = ClubCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Club created successfully.")
            return redirect('user_dashboard')
        else:
            messages.add_message(request, messages.ERROR, "This club name is already taken, please choose another one.")
    else:
        form = ClubCreationForm(initial = {'owner': request.user})
    return render(request, 'new_club.html', {'form': form})

@login_required
def edit_club(request, club_id):

    current_user = request.user

    try:
        current_user_membership = Membership.objects.get(user=current_user, club=club_id)
    except:
        current_user_membership = None

    if current_user_membership is None:
        messages.add_message(request, messages.ERROR, "Must be an owner and apart of this club to edit details!")
        return redirect('user_dashboard')

    if current_user_membership.user_type != "OW":
        messages.add_message(request, messages.ERROR, "Must be an owner to edit details!")
        return redirect('club_dashboard', club_id)

    try:
        current_club = Club.objects.get(id=club_id)
    except:
        current_club = None

    if request.method == 'POST':
        form = EditClubDetailsForm(instance=current_club, data=request.POST)

        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Club updated!")
            form.save()
            redirect_url = request.POST.get('next') or reverse('club_dashboard', kwargs={'club_id':current_club.id})
            return redirect(redirect_url)
        else:
            messages.add_message(request, messages.ERROR, "There is an error, please try again.")

    else:
        form = EditClubDetailsForm(instance=current_club)

    return render(request, 'edit_club.html', {'form': form, 'club': current_club})
