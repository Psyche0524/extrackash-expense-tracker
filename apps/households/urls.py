from django.urls import path

from . import views

urlpatterns = [
    path('explore/shared/', views.shared, name='shared'),
    path('explore/shared/new/', views.household_new, name='household_new'),
    path('explore/shared/invite/', views.household_invite, name='household_invite'),
    path('explore/shared/leave/', views.household_leave, name='household_leave'),
]
