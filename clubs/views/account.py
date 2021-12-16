'''Account Related Views'''
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from clubs.forms import EditProfileForm, ChangePasswordForm

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