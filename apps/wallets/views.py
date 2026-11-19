from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.core.utils import _daily_bars, _delete, _form_page, _insight, _set_user
from apps.transactions.models import Transaction
from apps.wallets.forms import AccountForm, TransferForm
from apps.wallets.models import Account


@login_required
def transfer(request):
    user = request.user
    accounts = list(user.accounts.all())
    first, second = (accounts + [None, None])[:2]
    form = TransferForm(user, request.POST or None, request.FILES or None, initial={
        'account': first, 'to_account': request.GET.get('to') or second,
    })
    if form.is_valid():
        tx = form.save(commit=False)
        tx.user, tx.kind, tx.category = user, 'transfer', 'other'
        tx.description = f'{tx.account or "Outside"} → {tx.to_account or "Outside"}'
        tx.save()
        if form.cleaned_data.get('fee'):
            Transaction.objects.create(user=user, kind='expense', category='fees', amount=form.cleaned_data['fee'],
                                       description='Transfer fee', account=tx.account, date=tx.date, time=tx.time)
        messages.success(request, 'Transfer recorded.')
        return redirect('accounts')
    return render(request, 'wallets/transfer.html', {'form': form, 'tab': 'wallet'})


def _net_change(t):
    """How much one transaction changes net worth (moves between your own accounts change nothing)."""
    if t.kind == 'income':
        return t.amount
    if t.kind == 'expense':
        return -t.amount
    return (t.amount if t.to_account_id else 0) - (t.amount if t.account_id else 0)


@login_required
def accounts(request):
    user = request.user
    show = request.GET.get('show', 'all')
    group = request.GET.get('group', '')
    account_list = list(user.accounts.all())
    for a in account_list:
        a.bal = a.balance
    assets = sum((a.bal for a in account_list if not a.is_liability), Decimal(0))
    liabilities = -sum((a.bal for a in account_list if a.is_liability), Decimal(0))
    net = assets - liabilities

    # Net worth at the end of each of the last 7 days = today's net worth minus what changed since.
    today = timezone.localdate()
    recent = list(user.transactions.filter(date__gt=today - timedelta(days=7)))
    daily = [(d.strftime('%a')[0], net - sum((_net_change(t) for t in recent if t.date > d), Decimal(0)))
             for d in (today - timedelta(days=i) for i in range(6, -1, -1))]

    shown = [a for a in account_list if show == 'all' or (show == 'liabilities') == a.is_liability]
    if group:
        shown = [a for a in shown if (a.group or 'Ungrouped') == group]
    groups = {}
    for a in shown:
        g = groups.setdefault(a.group or 'Accounts', {'name': a.group or 'Accounts', 'items': [], 'total': Decimal(0)})
        g['items'].append(a)
        g['total'] += a.bal
    return render(request, 'wallets/accounts.html', {
        'net': net, 'assets': assets, 'liabilities': liabilities, 'show': show, 'group': group,
        'group_names': sorted({a.group for a in account_list if a.group}), 'groups': groups.values(),
        'view': request.GET.get('view', 'grid'), 'daily': _daily_bars(daily), 'insight': _insight(user),
        'recent_income': user.transactions.filter(kind='income').select_related('account')[:5],
        'tab': 'wallet',
    })


@login_required
def account_new(request):
    return _form_page(request, AccountForm, 'Add wallet', 'accounts', on_save=_set_user(request),
                      initial={'kind': request.GET.get('kind', 'bank')})


@login_required
def account_edit(request, pk):
    account = get_object_or_404(Account, pk=pk, user=request.user)
    return _form_page(request, AccountForm, 'Edit account', 'accounts', instance=account)


@login_required
@require_POST
def account_delete(request, pk):
    return _delete(request, get_object_or_404(Account, pk=pk, user=request.user), 'accounts', 'Account')


@login_required
def cards(request):
    cards = []
    for a in request.user.accounts.filter(kind='credit'):
        owed = max(-a.balance, 0)
        limit = a.credit_limit or 0
        cards.append({'card': a, 'owed': owed, 'available': limit - owed, 'pct': int(owed / limit * 100) if limit else 0})
    return render(request, 'wallets/cards.html', {
        'cards': cards, 'installments': request.user.debts.filter(kind='installment').count(), 'tab': 'plan',
    })
