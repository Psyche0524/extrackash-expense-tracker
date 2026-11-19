from django import forms
from django.contrib.auth.models import User

from apps.core.forms import MONEY, UserForm
from apps.households.models import Household


class HouseholdForm(UserForm):
    class Meta:
        model = Household
        fields = ['name', 'shared_budget']
        widgets = {'shared_budget': MONEY}


class InviteForm(forms.Form):
    email = forms.EmailField(help_text='They need an Extrackash account first.')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            return User.objects.get(username=email)
        except User.DoesNotExist:
            raise forms.ValidationError('No Extrackash account uses this email yet.')
