from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from apps.accounts.forms import EmailLoginForm

# Each app keeps its own routes in apps/<name>/urls.py. URL names are global (no namespaces),
# so templates use {% url 'home' %}, {% url 'add' %}, etc.
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html', authentication_form=EmailLoginForm, redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('apps.accounts.urls')),
    path('', include('apps.dashboard.urls')),
    path('', include('apps.transactions.urls')),
    path('', include('apps.wallets.urls')),
    path('', include('apps.planning.urls')),
    path('', include('apps.debts.urls')),
    path('', include('apps.investments.urls')),
    path('', include('apps.reports.urls')),
    path('', include('apps.households.urls')),
    path('', include('apps.system_settings.urls')),
    path('admin/', admin.site.urls),
]
