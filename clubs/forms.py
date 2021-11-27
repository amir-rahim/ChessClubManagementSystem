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
        fields = ['username', 'name', 'email']

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
            password=self.cleaned_data.get('new_password')
        )
        return user


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

        if(self.data.get('user') != None):
            self.queryset = Club.objects.exclude(id__in = Membership.objects.filter(user = User.objects.get(id=self.data.get('user'))).values('club'))
        elif (self.initial.get('user') != None):
            self.queryset = Club.objects.exclude(id__in = Membership.objects.filter(user = self.initial['user'].id).values('club'))
            self.data['user'] = self.initial['user']
        else:
            self.queryset = Club.objects.all()


        self.fields['club'].queryset = self.queryset
        self.fields['club'].empty_label = None

    #queryset = None
    #club = forms.ModelChoiceField(
    #    queryset = queryset,
    #    empty_label=None,
    #    to_field_name="name")

    def clean(self):
        """Clean the data and generate messages for any errors."""
        super().clean()
        club = self.cleaned_data.get('club')
        if(self.cleaned_data.get('user') != None):
            user = self.cleaned_data.get('user')
        elif (self.initial.get('user') != None):
            user = self.initial.get('user')

    def save(self):
        """Create a new membership."""
        super().save(commit=False)
        if(self.cleaned_data.get('user') != None):
            user = self.cleaned_data.get('user')
        elif (self.initial.get('user') != None):
            user = self.initial.get('user')

        membership = Membership.objects.create(
            user = user,
            club = self.cleaned_data.get('club'),
            personal_statement = self.cleaned_data.get('personal_statement')

        )
        return membership



class ClubCreationForm(forms.ModelForm):
    """Form enabling logged user to create a new club."""
    class Meta:
        model = Club
        fields = ['name', 'owner']
        widgets = {
            'owner': forms.HiddenInput(attrs = {'is_hidden': True})
        }

class TournamentCreationForm(forms.ModelForm):
    """Form enabling officers to create Torunaments."""
    class Meta:
        model = Tournament
        fields = ['name', 'description', 'club', 'organizer']
        widgets = {
            'description': forms.Textarea(),
            'organizer': forms.HiddenInput(attrs = {'is_hidden': True}),
            'club': forms.HiddenInput(attrs = {'is_hidden': True})
        }

    class DateTimeInput(forms.DateTimeInput):
        input_type = 'datetime-local'


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
        if len(Membership.objects.filter(user = organizer, club = club)) > 0 and Membership.objects.get(user = organizer, club = club).user_type != 'OF':
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
            date=self.cleaned_data.get('date')
        )
        return tournament
