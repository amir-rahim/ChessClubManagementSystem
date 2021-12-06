from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse

from .models import Membership, Club, User
from .forms import LogInForm, SignUpForm, MembershipApplicationForm, ClubCreationForm, TournamentCreationForm, EditProfileForm, EditClubDetailsForm, ChangePasswordForm
from .helpers import login_prohibited

from .models import User


# Create your views here.

@login_prohibited
def home(request):
    return render(request, 'home.html')

@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                redirect_url = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
                return redirect(redirect_url)

        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")

    form = LogInForm()
    next = request.GET.get('next') or ''
    return render(request, 'log_in.html', {'form': form, 'next': next})

@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    else:
        form = SignUpForm()

    return render(request, 'sign_up.html', {'form': form})

@login_required
def user_dashboard(request):
    data = {'user': request.user}
    return render(request, 'user_dashboard.html', data)

@login_required
def user_profile(request):
    if request.method == 'POST':
        membership = Membership.objects.get(pk = request.POST['membership'])
        data = {'user' : membership.user, 'membership' : membership}
    else : 
        data = {'user': request.user, "my_profile" : True}
    return render(request, 'user_profile.html', data)

@login_required
def edit_user_profile(request):
    current_user = request.user

    if request.method == 'POST':
        form = EditProfileForm(instance=current_user, data=request.POST)

        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            redirect_url = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
            return redirect(redirect_url)

    else:
        form = EditProfileForm(instance=current_user)

    return render(request, 'edit_user_profile.html', {'form': form})

@login_required
def change_password(request):
    current_user = request.user

    if request.method == 'POST':
        form = ChangePasswordForm(data=request.POST)

        if form.is_valid():
            password = form.cleaned_data.get('current_password')

            if current_user.check_password(password):
                new_password = form.cleaned_data.get('new_password')
                current_user.set_password(new_password)
                current_user.save()
                login(request, current_user)
                messages.add_message(request, messages.SUCCESS, "Password updated!")
                return redirect('user_profile')
            else:
                messages.add_message(request, messages.ERROR, "Password has not been updated as current password is incorrect! Try again!")
        else:
                messages.add_message(request, messages.ERROR, "Password has not been updated as form is incorrect! Try again!")
    
    form = ChangePasswordForm()
    
    return render(request, 'change_password.html', {'form': form})

def log_out(request):
    logout(request)
    return redirect('home')

@login_required
def club_user_list(request):
    model = User
    user = User.objects.all()
    return render(request, 'club_user_list.html', {'users': user  })

@login_required
def membership_application(request):
    if request.method == 'POST':
        form = MembershipApplicationForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Application sent successfully.")
            return redirect('user_dashboard')
        else:
            if form.data.get('personal_statement').strip() == "":
                messages.add_message(request, messages.ERROR, "Please enter a valid personal statement.")
            else:
                messages.add_message(request, messages.ERROR, "There is an error with the form, please try again.")
    else:
        form = MembershipApplicationForm(initial = {'user': request.user})
        if form.fields['club'].queryset.count() == 0:
            messages.add_message(request, messages.ERROR, "Cannot apply to any club. You already applied to every club available.")
            return redirect('user_dashboard')
    return render(request, 'apply.html', {'form': form})

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

@login_required
def tournament_creation(request, club_id):
    club = Club.objects.get(id = club_id)
    if request.method == 'POST':
        form = TournamentCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Tournament created successfully.")
            return redirect('user_dashboard')
        else:
            if form.errors['organizer'] != None:
                messages.add_message(request, messages.ERROR, form.errors['organizer'])
                return redirect('user_dashboard')
    else:
        form = TournamentCreationForm(initial = {'organizer': request.user, 'club': club})
    return render(request, 'new_tournament.html', {'form': form, 'club': club})

@login_required
def available_clubs(request):
    query = Club.objects.all()
    list_of_clubs = []
    for club in query:
        owner = club.owner
        list_of_clubs.append({"name":club.name, "owner":owner.name, "club_id":club.id})
    return render(request, 'available_clubs.html', {'list_of_clubs': list_of_clubs})

@login_required
def club_memberships(request):
    memberships = Membership.objects.filter(user=request.user)
    clubs = [membership.club for membership in memberships]
    return render(request, 'club_memberships.html', {'clubs': clubs})

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
        messages.add_message(request, messages.ERROR, "Error transferring ownership." + str(e))

    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return HttpResponse(status = 200)

@login_required
def leave_club(request, club_id):
    current_user = request.user
    club = Club.objects.get(id=club_id)
    try:
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

    return render(request, 'club_dashboard.html', {
        'club': club,
        'membership': membership,
        'members': members,
        'officers': officers,
        'applications': applications
    })


@login_required
def my_applications(request):
    user = request.user
    messages = []
    applications_info = []
    try:
        applications = Membership.objects.filter(user=user)
        for application in applications:
            application_status = application.application_status
            if application_status == 'P':
                application_status = "Pending"
            elif application_status == 'A':
                application_status = "Approved"
            else: #'D'
                application_status = "Denied"
            applications_info.append({"club_name":application.club.name, "club_id":application.club.id, "application_status":application_status})
    except:
        pass
    return render(request, 'my_applications.html', {'applications_info': applications_info})


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
