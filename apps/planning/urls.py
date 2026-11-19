from django.urls import path

from . import views

urlpatterns = [
    path('plan/', views.plan, name='plan'),
    path('plan/budgets/', views.budgets, name='budgets'),
    path('plan/budgets/new/', views.budget_new, name='budget_new'),
    path('plan/planned/', views.planned, name='planned'),
    path('plan/planned/new/', views.planned_new, name='planned_new'),
    path('plan/planned/<int:pk>/edit/', views.planned_edit, name='planned_edit'),
    path('plan/planned/<int:pk>/done/', views.planned_done, name='planned_done'),
    path('plan/planned/<int:pk>/delete/', views.planned_delete, name='planned_delete'),
    path('plan/travel/', views.trips, name='trips'),
    path('plan/travel/new/', views.trip_new, name='trip_new'),
    path('plan/travel/<int:pk>/edit/', views.trip_edit, name='trip_edit'),
    path('plan/travel/<int:pk>/delete/', views.trip_delete, name='trip_delete'),
    path('plan/tags/', views.tags, name='tags'),
    path('plan/budgets/<int:pk>/', views.budget_detail, name='budget'),
    path('plan/budgets/<int:pk>/edit/', views.budget_edit, name='budget_edit'),
    path('plan/budgets/<int:pk>/delete/', views.budget_delete, name='budget_delete'),
    path('plan/goals/', views.goals, name='goals'),
    path('plan/goals/new/', views.goal_new, name='goal_new'),
    path('plan/goals/<int:pk>/', views.goal_detail, name='goal'),
    path('plan/goals/<int:pk>/edit/', views.goal_edit, name='goal_edit'),
    path('plan/goals/<int:pk>/add/', views.goal_add_money, name='goal_add'),
    path('plan/goals/<int:pk>/delete/', views.goal_delete, name='goal_delete'),
    path('plan/cashflow/', views.cashflow, name='cashflow'),
]
