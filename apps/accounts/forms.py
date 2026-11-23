from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, UserCreationForm
from django.contrib.auth.models import User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email']
        labels = {'first_name': 'Your name'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(username=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        self.instance.username = self.cleaned_data['email']  # email is the login
        return super().save(commit)


class SignUpForm(UserCreationForm):
    """Sign up with name + email; the email is stored as the username."""

    first_name = forms.CharField(label='Your name', max_length=150, widget=forms.TextInput(attrs={'autocomplete': 'given-name'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

    class Meta:
        model = User
        fields = ['first_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password2'].label = 'Confirm password'

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class EmailLoginForm(AuthenticationForm):
    """Log in with your email (normal sign-ups) or your username (e.g. a superuser made with createsuperuser)."""

    username = forms.CharField(label='Email or username', max_length=254,
                               widget=forms.TextInput(attrs={'autofocus': True, 'autocomplete': 'username'}))

    def clean(self):
        login = (self.cleaned_data.get('username') or '').strip()
        if '@' in login:
            # Sign-ups store the lower-cased email as their username; a superuser's email is a separate field.
            login = login.lower()
            if not User.objects.filter(username=login).exists():
                match = User.objects.filter(email__iexact=login).first()
                if match:
                    login = match.username
        self.cleaned_data['username'] = login
        return super().clean()


class NewPasswordForm(SetPasswordForm):
    """Forgot-password 'choose a new password' form, labelled like Sign up."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password2'].label = 'Confirm new password'
