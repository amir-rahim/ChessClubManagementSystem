"""Forms for the clubs app."""
from django import forms
from django.core.validators import RegexValidator
from .models import User, Membership, Club

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
    #queryset = Club.objects.exclude(id__in = Membership.objects.filter(user = initial['user'].id).values('club'))
    queryset = Club.objects.all()
    #user = None
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

        if(self.initial.get('user') == None):
            self.queryset = Club.objects.exclude(id__in = Membership.objects.filter(user = self.user.id).values('club'))
        else:
            self.queryset = Club.objects.exclude(id__in = Membership.objects.filter(user = self.initial['user'].id).values('club'))

        self.fields['club'].queryset = self.queryset


    club = forms.ModelChoiceField(
        queryset = queryset,
        empty_label=None,
        to_field_name="name")

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        club = self.cleaned_data.get('club')



class ClubCreationForm(forms.ModelForm):
    """Form enabling logged user to create a new club."""
    class Meta:
        model = Club
        fields = ['name', 'owner']
        widgets = {
            'owner': forms.HiddenInput(attrs = {'is_hidden': True})
        }
