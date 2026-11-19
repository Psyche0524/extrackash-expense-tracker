from django.urls import path

from . import views

urlpatterns = [
    path('transfer/', views.transfer, name='transfer'),
    path('explore/accounts/', views.accounts, name='accounts'),
    path('explore/accounts/new/', views.account_new, name='account_new'),
    path('explore/accounts/<int:pk>/edit/', views.account_edit, name='account_edit'),
    path('explore/accounts/<int:pk>/delete/', views.account_delete, name='account_delete'),
    path('explore/cards/', views.cards, name='cards'),
]
