from django.urls import path

from . import views

urlpatterns = [
    path('explore/reports/', views.reports, name='reports'),
    path('explore/reports/export.csv', views.export_csv, name='export'),
]
