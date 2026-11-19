from django.urls import path

from . import views

urlpatterns = [
    path('activity/', views.activity, name='activity'),
    path('activity/<int:pk>/', views.transaction_detail, name='transaction'),
    path('activity/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('activity/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    path('activity/<int:pk>/photo/', views.transaction_photo, name='transaction_photo'),
    path('add/', views.add_transaction, name='add'),
]
