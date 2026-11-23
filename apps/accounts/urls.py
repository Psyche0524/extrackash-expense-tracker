from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import EmailLoginForm, NewPasswordForm

urlpatterns = [
    path('welcome/', views.welcome, name='welcome'),
    path('signup/', views.signup, name='signup'),
    # Log in / log out use Django's built-in views with our email form and login.html page.
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html', authentication_form=EmailLoginForm, redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Forgot password: Django's built-in reset flow (one-time link by email, expires after an hour).
    path('password/forgot/', auth_views.PasswordResetView.as_view(
        template_name='forgot_password.html',
        email_template_name='emails/password_reset.txt',
        subject_template_name='emails/password_reset_subject.txt',
    ), name='password_reset'),
    path('password/forgot/sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='forgot_password_sent.html'), name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='reset_password.html', form_class=NewPasswordForm), name='password_reset_confirm'),
    path('password/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='reset_password_done.html'), name='password_reset_complete'),
    path('setup/', views.setup, name='setup'),
    path('ready/', views.ready, name='ready'),
    path('settings/profile/', views.profile_edit, name='profile_edit'),
]
