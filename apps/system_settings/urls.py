from django.urls import path

from . import views

urlpatterns = [
    path('explore/', views.explore, name='explore'),
    path('settings/', views.settings_page, name='settings'),
    path('settings/delete/', views.delete_account, name='delete_account'),
    path('backup/download/', views.download_full_backup, name='download_backup'),
]