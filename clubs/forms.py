"""Forms for the clubs app."""
from django import forms
from django.core.validators import RegexValidator
from .models import User, Membership, Club, Tournament

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())


class SignUpForm(forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['username', 'name', 'email', 'public_bio', 'chess_experience']
        widgets = {
            'public_bio': forms.Textarea(),
        }

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            name=self.cleaned_data.get('name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            public_bio=self.cleaned_data.get('public_bio'),
            chess_experience=self.cleaned_data.get('chess_experience')
        )
        return user

class EditProfileForm(forms.ModelForm):
    """Form enabling users to edit their profile."""

    class Meta:
        """Form options."""

        model = User
        fields = ['username', 'name', 'email', 'public_bio', 'chess_experience']
        widgets = {
            'public_bio': forms.Textarea(),
        }

class ChangePasswordForm(forms.ModelForm):
    """Form enabling users to change their password."""

    class Meta:
        """Form options."""

        model = User
        fields = []

    current_password = forms.CharField(label='Current password', widget=forms.PasswordInput())
    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

class EditClubDetailsForm(forms.ModelForm):
    """Form enabling owners to edit their club details."""

    class Meta:
        """Form options."""

        model = Club
        fields = ['name', 'owner', 'location', 'mission_statement', 'description']
        widgets = {
            'owner': forms.HiddenInput(attrs = {'is_hidden': True})
        }

class MembershipApplicationForm(forms.ModelForm):
    """Form enabling logged user to apply for a membership."""
    class Meta:
        model = Membership
        fields = ['club', 'user', 'personal_statement']
        widgets = {
            'user': forms.HiddenInput(attrs = {'is_hidden': True}),
            'personal_statement': forms.Textarea(),
        }

    def __init__(self, *args, **kwargs):
        """Change label for selector """
        super(MembershipApplicationForm, self).__init__(*args, **kwargs)
        self.fields['club'].label_from_instance = lambda instance: instance.name

        """Querying database and retrieving all clubs which a user can apply for (ie: all clubs the user is not a member, officer, or owner at)"""
        if (self.initial.get('user') != None):
            self.queryset = Club.objects.exclude(id__in = Membership.objects.filter(user = self.initial['user'].id).values('club'))
            self.data['user'] = self.initial['user']
        else:
            self.queryset = Club.objects.exclude(id__in = Membership.objects.filter(user = User.objects.get(id=self.data.get('user'))).values('club'))

        """Displaying all available clubs to the user"""
        self.fields['club'].queryset = self.queryset
        self.fields['club'].empty_label = None

    def clean(self):
        """Clean the data and generate messages for any errors."""
        super().clean()
        club = self.cleaned_data.get('club')
        user = self.cleaned_data.get('user')


    def save(self):
        """Create a new membership."""
        super().save(commit=False)

        membership = Membership.objects.create(
            user = self.cleaned_data.get('user'),
            club = self.cleaned_data.get('club'),
            personal_statement = self.cleaned_data.get('personal_statement')

        )
        return membership



class ClubCreationForm(forms.ModelForm):
    """Form enabling logged user to create a new club."""
    class Meta:
        model = Club
        fields = ['name', 'owner', 'location', 'mission_statement', 'description']
        widgets = {
            'owner': forms.HiddenInput(attrs = {'is_hidden': True})
        }

class TournamentCreationForm(forms.ModelForm):
    """Form enabling officers to create Torunaments."""

    class Meta:
        model = Tournament
        fields = ['name', 'description', 'club', 'organizer', 'coorganizers']
        widgets = {
            'description': forms.Textarea(),
            'organizer': forms.HiddenInput(attrs = {'is_hidden': True}),
            'club': forms.HiddenInput(attrs = {'is_hidden': True}),
            'coorganizers': forms.CheckboxSelectMultiple()
        }

    class DateTimeInput(forms.DateTimeInput):
        input_type = 'datetime-local'

    def __init__(self, *args, **kwargs):
        super(TournamentCreationForm, self).__init__(*args, **kwargs)
        """Querying database and retrieving all users which can create Torunaments (ie: all officers and owners at a club)"""
        if (self.initial.get('club') != None):
            self.data['club'] = self.initial['club']
            self.data['organizer'] = self.initial['organizer']

        """Displaying all officers and owners which can co-organize"""
        self.fields['coorganizers'].queryset = User.objects.filter(id__in =
                Membership.objects.filter(
                    club=self.data.get('club'),
                    user_type__in = [Membership.UserTypes.OWNER, Membership.UserTypes.OFFICER]
                )
                .exclude(user = self.data.get('organizer'))
                .values('user')
            )

    date = forms.DateTimeField(widget = DateTimeInput())
    deadline = forms.DateTimeField(widget = DateTimeInput())
    capacity = forms.IntegerField()

    def clean(self):
        """Clean the data and generate messages for any errors."""
        super().clean()
        date = self.cleaned_data.get('date')
        deadline = self.cleaned_data.get('deadline')
        capacity = self.cleaned_data.get('capacity')
        club = self.cleaned_data.get('club')
        organizer = self.cleaned_data.get('organizer')


        if deadline != None and date != None and deadline >= date:
            self.add_error('date', 'Tournament date must be after application deadline.')
        if capacity<2 or capacity>96:
            self.add_error('capacity', 'Capacity must be a number between 2 and 96')
        if len(Membership.objects.filter(user = organizer, club = club)) <= 0 or Membership.objects.get(user = organizer, club = club).user_type != 'OF':
            self.add_error('organizer', "You don't have sufficient permissions to create a tournament.")

    def save(self):
        """Create a new tournament."""
        super().save(commit=False)

        tournament = Tournament.objects.create(
            name=self.cleaned_data.get('name'),
            description=self.cleaned_data.get('description'),
            organizer=self.cleaned_data.get('organizer'),
            club=self.cleaned_data.get('club'),
            deadline=self.cleaned_data.get('deadline'),
            capacity=self.cleaned_data.get('capacity'),
            date=self.cleaned_data.get('date'),
        )
        for c in self.cleaned_data.get('coorganizers'):
            tournament.coorganizers.add(c)
        tournament.save()
        return tournament
