from django.urls import path

from . import views

urlpatterns = [
    path('explore/', views.explore, name='explore'),
    path('settings/', views.settings_page, name='settings'),
    path('settings/delete/', views.delete_account, name='delete_account'),
    path('backup/download/', views.download_full_backup, name='download_backup'),
    # admin dashboard, superusers only
    path('settings/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('settings/admin/users/', views.admin_users, name='admin_users'),
    path('settings/admin/users/<int:pk>/', views.admin_user, name='admin_user'),
    path('settings/admin/users/<int:pk>/toggle/', views.admin_user_toggle, name='admin_user_toggle'),
    path('settings/admin/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
]
