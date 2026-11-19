from django.urls import path

from . import views

urlpatterns = [
    path('welcome/', views.welcome, name='welcome'),
    path('signup/', views.signup, name='signup'),
    path('setup/', views.setup, name='setup'),
    path('ready/', views.ready, name='ready'),
    path('settings/profile/', views.profile_edit, name='profile_edit'),
]
