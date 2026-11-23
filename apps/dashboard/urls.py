from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shared/', views.shared, name='shared'),
]