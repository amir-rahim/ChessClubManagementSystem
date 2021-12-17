'''Memberships Related Views'''
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, Q, OuterRef

from clubs.forms import MembershipApplicationForm
from clubs.models import Membership, Club

@login_required
def membership_application(request):
    """Successfull applications will pass and redirect user to user dashboard and let the user know, whereas invalid applications will notify the user."""
    if request.method == 'POST':
        form = MembershipApplicationForm(data=request.POST)
        if form.is_valid():
            # The membership-application-form is valid, it is saved as a 'pending' Membership object in the database
            form.save()
            messages.add_message(request, messages.SUCCESS, "Application sent successfully.")
            return redirect('user_dashboard')
        else:
            if form.data.get('personal_statement') and form.data.get('personal_statement').strip() == "":
                # The form contains an empty personal statement, an error message is output
                messages.add_message(request, messages.ERROR, "Please enter a valid personal statement.")
            else:
                messages.add_message(request, messages.ERROR, "There is an error with the form, please try again.")
    else:
        form = MembershipApplicationForm(initial = {'user': request.user})
        if form.fields['club'].queryset.count() == 0:
            # The user has already applied to every club available, it cannot apply to any other club, an error message is output
            messages.add_message(request, messages.ERROR, "Cannot apply to any club. You already applied to every club available.")
            return redirect('user_dashboard')
    return render(request, 'apply.html', {'form': form})

@login_required
def my_applications(request):
    """Allow user to view the status of their applications to clubs"""
    # Get currently logged-in user
    user = request.user
    messages = []
    applications_info = []
    try:
        # Get the list of all applications for the logged-in user
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
def club_memberships(request):
    """Show a list of all clubs the user is member of."""
    # Select clubs the user is a member of
    subquery = Membership.objects.filter(user=request.user.pk, club=OuterRef('pk'))
    clubs = Club.objects.filter(
        Q(Exists(subquery)) &
        ~Q(Exists(subquery.filter(user_type=Membership.UserTypes.NON_MEMBER)))
    )
    return render(request, 'club_memberships.html', {'clubs': clubs})

@login_required
def available_clubs(request):
    """Show a list of all clubs the user can apply to (all clubs the user is not member of)."""
    # Select clubs the user is not a member of
    subquery = Membership.objects.filter(user=request.user.pk, club=OuterRef('pk'))
    clubs = Club.objects.filter(
        ~Q(Exists(subquery)) |
        Q(Exists(subquery.filter(user_type=Membership.UserTypes.NON_MEMBER)))
    )
    return render(request, 'available_clubs.html', {'clubs': clubs})
