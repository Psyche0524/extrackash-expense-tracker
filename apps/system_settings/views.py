import io
from datetime import datetime, timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.db.models import Count, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.core.utils import _month_start, _sum
from apps.households.models import Household
from apps.transactions.models import Transaction
from apps.wallets.models import Account

User = get_user_model()


def superuser_required(view):
    """Superusers only. Everyone else gets 'page not found', so admin pages don't reveal they exist."""
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404
        return view(request, *args, **kwargs)
    return wrapper


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


@superuser_required
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


# ---------- admin dashboard (superusers only) ----------

@superuser_required
def admin_dashboard(request):
    now = timezone.now()
    month = Transaction.objects.filter(date__gte=_month_start())
    return render(request, 'admin_dashboard.html', {
        'users': User.objects.count(),
        'new_users': User.objects.filter(date_joined__gte=_month_start()).count(),
        'active_users': User.objects.filter(last_login__gte=now - timedelta(days=30)).count(),
        'superusers': User.objects.filter(is_superuser=True).count(),
        'transactions': Transaction.objects.count(),
        'accounts': Account.objects.count(),
        'households': Household.objects.count(),
        'month_income': _sum(month.filter(kind='income')),
        'month_expense': _sum(month.filter(kind='expense')),
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'tab': 'plan',
    })


@superuser_required
def admin_users(request):
    q, show = request.GET.get('q', '').strip(), request.GET.get('show', 'all')
    people = User.objects.annotate(tx_count=Count('transactions')).order_by('-date_joined')
    if q:
        people = people.filter(Q(first_name__icontains=q) | Q(email__icontains=q) | Q(username__icontains=q))
    people = {'active': people.filter(is_active=True), 'inactive': people.filter(is_active=False),
              'superusers': people.filter(is_superuser=True)}.get(show, people)
    return render(request, 'admin_users.html', {'people': people, 'q': q, 'show': show, 'tab': 'plan'})


@superuser_required
def admin_user(request, pk):
    person = get_object_or_404(User, pk=pk)
    return render(request, 'admin_user.html', {
        'person': person,
        'counts': [
            ('Accounts', person.accounts.count()), ('Transactions', person.transactions.count()),
            ('Budgets', person.budgets.count()), ('Goals', person.goals.count()),
            ('Debts & installments', person.debts.count()), ('Investments', person.investments.count()),
        ],
        'recent': person.transactions.select_related('account')[:8],
        'is_me': person == request.user,
        'tab': 'plan',
    })


@superuser_required
@require_POST
def admin_user_toggle(request, pk):
    person = get_object_or_404(User, pk=pk)
    if person == request.user:
        messages.error(request, "You can't deactivate your own account here.")
    else:
        person.is_active = not person.is_active
        person.save(update_fields=['is_active'])
        messages.success(request, f"{person.first_name or person.email} is now {'active' if person.is_active else 'deactivated'}.")
    return redirect('admin_user', pk=pk)


@superuser_required
@require_POST
def admin_user_delete(request, pk):
    person = get_object_or_404(User, pk=pk)
    if person == request.user:
        messages.error(request, "You can't delete your own account here. Use Settings → Delete my account.")
        return redirect('admin_user', pk=pk)
    name = person.first_name or person.email
    person.delete()  # cascades to all of their records
    messages.success(request, f'{name} and all their records were deleted.')
    return redirect('admin_users')
