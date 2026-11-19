from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


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
