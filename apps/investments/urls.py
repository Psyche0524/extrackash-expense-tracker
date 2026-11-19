from django.urls import path

from . import views

urlpatterns = [
    path('explore/investments/', views.investments, name='investments'),
    path('explore/investments/new/', views.investment_new, name='investment_new'),
    path('explore/investments/<int:pk>/edit/', views.investment_edit, name='investment_edit'),
    path('explore/investments/<int:pk>/delete/', views.investment_delete, name='investment_delete'),
]
