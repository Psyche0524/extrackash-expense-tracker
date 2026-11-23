import io
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.management import call_command
from django.http import HttpResponse
from django.shortcuts import redirect, render


def is_superuser(user):
    return user.is_authenticated and user.is_superuser


def explore(request):
    return redirect('plan')  # Explore was merged into the Plan hub; keep old links working.


@login_required
def settings_page(request):
    return render(request, 'settings.html', {'tab': 'plan'})


@login_required
def delete_account(request):
    if request.method == 'POST' and request.POST.get('confirm') == 'DELETE':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account and data were deleted.')
        return redirect('welcome')
    return render(request, 'delete_account.html', {'tab': 'plan'})


@user_passes_test(is_superuser)
def download_full_backup(request):
    buffer = io.StringIO()

    call_command(
        'dumpdata',
        exclude=['contenttypes', 'auth.permission', 'sessions.session', 'admin.logentry'],
        indent=2,
        stdout=buffer,
    )

    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    filename = f'extrackash_backup_{timestamp}.json'

    response = HttpResponse(buffer.getvalue(), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response