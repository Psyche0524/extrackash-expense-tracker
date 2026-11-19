from django.urls import path

from . import views

urlpatterns = [
    path('explore/installments/', views.debts, {'kind': 'installment'}, name='installments'),
    path('explore/loans/', views.debts, {'kind': 'loan'}, name='loans'),
    path('explore/receivables/', views.debts, {'kind': 'receivable'}, name='receivables'),
    path('explore/debts/new/', views.debt_new, name='debt_new'),
    path('explore/debts/<int:pk>/edit/', views.debt_edit, name='debt_edit'),
    path('explore/debts/<int:pk>/pay/', views.debt_pay, name='debt_pay'),
    path('explore/debts/<int:pk>/delete/', views.debt_delete, name='debt_delete'),
]
