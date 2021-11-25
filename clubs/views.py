from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import Membership, Club, User
from .forms import LogInForm, SignUpForm, MembershipApplicationForm, ClubCreationForm
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
    data = {'user': request.user}
    return render(request, 'user_profile.html', data)

def log_out(request):
    logout(request)
    return redirect('home')


def club_user_list(request):
    model = User
    user = User.objects.all()
    return render(request, 'club_user_list.html', {'users': user  })

@login_required
def membership_application(request):
    if request.method == 'POST':
        form = MembershipApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_dashboard')
        else:
            messages.add_message(request, messages.ERROR, "You already applied for this club. Please apply to a different one.")
    else:
        form = MembershipApplicationForm(initial = {'user': request.user})
    return render(request, 'apply.html', {'form': form})

@login_required
def club_creation(request):
    if request.method == 'POST':
        form = ClubCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_dashboard')
        #else:
        #    messages.add_message(request, messages.ERROR, "This club name is already taken, please choose another one.")
    else:
        form = ClubCreationForm(initial = {'owner': request.user})
    return render(request, 'new_club.html', {'form': form})

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
def club_dashboard(request, id):
    user = request.user

    membership = None

    try:
        club = Club.objects.get(id=id)
    except:
        club = None

    if club is not None:

 

        membership = Membership.objects.filter(user=user, club=club).first()

        is_member = membership != None

        if is_member:
            is_officer = membership.user_type == "OF" or membership.user_type == "OW"
            is_owner = membership.user_type == "OW"

        members = Membership.objects.filter(club=club)

    return render(request, 'club_dashboard.html', {
        'club': club,
        'membership': membership,
        'members': members
    })
