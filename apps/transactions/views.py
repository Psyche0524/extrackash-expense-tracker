from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.core.utils import _add_months, _delete
from apps.transactions.forms import TransactionForm
from apps.transactions.models import Transaction
from apps.wallets.forms import TransferForm


@login_required
def activity(request):
    """History: filter by text, date, type, account or tag; grouped by day with totals."""
    f = request.GET
    txs = request.user.transactions.select_related('account', 'to_account')
    if f.get('q'):
        q = f['q'].strip()
        txs = txs.filter(Q(description__icontains=q) | Q(note__icontains=q) | Q(amount__icontains=q) | Q(category__icontains=q))
    if f.get('date'):
        txs = txs.filter(date=f['date'])
    if f.get('kind') in ('expense', 'income', 'transfer'):
        txs = txs.filter(kind=f['kind'])
    if f.get('account', '').isdigit():
        txs = txs.filter(Q(account_id=f['account']) | Q(to_account_id=f['account']))
    if f.get('tag'):
        txs = txs.filter(tags__icontains=f['tag'])
    days = {}
    for t in txs:
        day = days.setdefault(t.date, {'date': t.date, 'items': [], 'out': Decimal(0), 'in': Decimal(0)})
        day['items'].append(t)
        if t.kind == 'expense':
            day['out'] += t.amount
        elif t.kind == 'income':
            day['in'] += t.amount
    return render(request, 'transactions/activity.html', {
        'days': days.values(), 'f': f, 'accounts': request.user.accounts.all(), 'filtered': any(f.values()),
        'today': timezone.localdate(),
        'tab': 'activity',
    })


@login_required
def add_transaction(request):
    user = request.user
    if not user.accounts.exists():
        messages.info(request, 'Add an account first.')
        return redirect('account_new')
    form = TransactionForm(user, request.POST or None, request.FILES or None, initial={
        'kind': request.GET.get('kind', Transaction.EXPENSE),
        'account': user.accounts.first(),
    })
    if form.is_valid():
        tx = form.save(commit=False)
        tx.user = user
        tx.save()
        data = form.cleaned_data
        if data.get('recurring'):
            user.planned.create(kind=tx.kind, name=tx.description, amount=tx.amount, category=tx.category,
                                account=tx.account, next_date=_add_months(tx.date, 1), repeat='monthly')
        if data.get('owed_amount'):
            user.debts.create(kind='receivable', name=data['owed_by'], total=data['owed_amount'],
                              monthly=data['owed_amount'], account=tx.account, note=f'For {tx.description}')
        messages.success(request, 'Income saved.' if tx.kind == 'income' else 'Expense saved.')
        return redirect('activity')
    return render(request, 'transactions/add.html', {'form': form, 'tab': 'activity', 'scan': 'scan' in request.GET})


@login_required
def transaction_photo(request, pk):
    tx = get_object_or_404(Transaction, pk=pk, user=request.user)
    if not tx.photo:
        raise Http404
    return FileResponse(tx.photo.open('rb'))


@login_required
def transaction_detail(request, pk):
    tx = get_object_or_404(Transaction, pk=pk, user=request.user)
    return render(request, 'transactions/transaction.html', {'t': tx, 'tab': 'activity'})


@login_required
def transaction_edit(request, pk):
    tx = get_object_or_404(Transaction, pk=pk, user=request.user)
    is_transfer = tx.kind == 'transfer'
    form_class = TransferForm if is_transfer else TransactionForm
    form = form_class(request.user, request.POST or None, request.FILES or None, instance=tx)
    if form.is_valid():
        form.save()
        messages.success(request, 'Saved.')
        return redirect('transaction', pk=tx.pk)
    return render(request, 'wallets/transfer.html' if is_transfer else 'transactions/add.html', {'form': form, 'tab': 'activity'})


@login_required
@require_POST
def transaction_delete(request, pk):
    return _delete(request, get_object_or_404(Transaction, pk=pk, user=request.user), 'activity', 'Transaction')
