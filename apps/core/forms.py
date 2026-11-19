from django import forms


DATE = forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')


MONEY = forms.NumberInput(attrs={'step': '0.01', 'inputmode': 'decimal', 'placeholder': '0.00'})


class UserForm(forms.ModelForm):
    """ModelForm that only offers the current user's accounts in account dropdowns."""

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('account', 'to_account'):
            if name in self.fields:
                self.fields[name].queryset = user.accounts.all()


def positive(form, name):
    value = form.cleaned_data[name]
    if value is not None and value <= 0:
        raise forms.ValidationError('Must be more than 0.')
    return value


TIME = forms.TimeInput(attrs={'type': 'time'}, format='%H:%M')


PHOTO = forms.ClearableFileInput(attrs={'accept': 'image/*'})


MAX_PHOTO = 5 * 1024 * 1024


def check_photo(form):
    photo = form.cleaned_data.get('photo')
    if photo and hasattr(photo, 'content_type'):  # a new upload, not the saved file
        if not photo.content_type.startswith('image/'):
            raise forms.ValidationError('Please choose an image.')
        if photo.size > MAX_PHOTO:
            raise forms.ValidationError('Photo is too big (5 MB max).')
    return photo
