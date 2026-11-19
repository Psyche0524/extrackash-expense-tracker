from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.accounts.forms import ProfileForm, SignUpForm
from apps.wallets.forms import AccountForm


def welcome(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'accounts/welcome.html')


def signup(request):
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        login(request, form.save())
        return redirect('setup')
    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def setup(request):
    form = AccountForm(request.user, request.POST or None)
    if form.is_valid():
        account = form.save(commit=False)
        account.user = request.user
        account.save()
        return redirect('ready')
    return render(request, 'accounts/setup.html', {'form': form})


@login_required
def ready(request):
    return render(request, 'accounts/ready.html')


@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, 'Your preferences are saved.')
        return redirect('settings')
    return render(request, 'form.html', {'form': form, 'title': 'Edit profile', 'subtitle': 'Your email is also how you log in.'})
