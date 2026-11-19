from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import EmailLoginForm

urlpatterns = [
    path('welcome/', views.welcome, name='welcome'),
    path('signup/', views.signup, name='signup'),
    # Log in / log out use Django's built-in views with our email form and login.html page.
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html', authentication_form=EmailLoginForm, redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('setup/', views.setup, name='setup'),
    path('ready/', views.ready, name='ready'),
    path('settings/profile/', views.profile_edit, name='profile_edit'),
]
