from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import Membership, Club, User
from .forms import LogInForm, SignUpForm, MembershipApplicationForm
from .helpers import login_prohibited

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

@login_required
def membership_application(request):
    if request.method == 'POST':
        form = MembershipApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_dashboard')
        else:
            messages.add_message(request, messages.ERROR, "You already applied for this club. Please apply to a different one.")

    form = MembershipApplicationForm(initial = {'user': request.user})
    return render(request, 'apply.html', {'form': form})

@login_required
def available_clubs(request):
    query = Club.objects.all()
    list_of_clubs = []
    for club in query:
        owner = club.owner
        list_of_clubs.append({"name":club.name, "owner":owner.name, "club_id":club.id})
    return render(request, 'available_clubs.html', {'list_of_clubs': list_of_clubs})

@login_required
def club_dashboard(request, club_id):
    user = request.user

    try:
        club = Club.objects.get(id=club_id)
    except:
        club = None

    if club is not None:
        is_member = club.is_member(user)
        is_owner = club.owner == user
        members = club.get_members()

    return render(request, 'club_dashboard.html', {
        'club': club, 
        'is_member': is_member,
        'is_owner': is_owner,
        'members': members
    })
