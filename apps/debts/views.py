from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core.utils import _delete, _form_page, _set_user
from apps.debts.forms import DebtForm
from apps.debts.models import Debt
from apps.transactions.models import Transaction


@login_required
def debts(request, kind):
    debt_list = list(request.user.debts.filter(kind=kind).select_related('account'))
    for d in debt_list:
        d.pct = min(int(d.paid / d.total * 100), 100)
    active = [d for d in debt_list if d.remaining > 0]
    return render(request, 'debts.html', {
        'debts': debt_list, 'kind': kind, 'monthly': sum(min(d.monthly, d.remaining) for d in active),
        'remaining': sum(d.remaining for d in active), 'tab': 'plan',
    })


DEBT_TITLES = {'installment': 'Track installment', 'loan': 'Add loan', 'receivable': 'Someone owes me'}


@login_required
def debt_new(request):
    kind = request.GET.get('kind', 'installment')
    return _form_page(request, DebtForm, DEBT_TITLES.get(kind, 'Add'),
                      lambda d: f'/explore/{d.kind}s/', on_save=_set_user(request), initial={'kind': kind})


@login_required
def debt_edit(request, pk):
    debt = get_object_or_404(Debt, pk=pk, user=request.user)
    return _form_page(request, DebtForm, 'Adjust plan', lambda d: f'/explore/{d.kind}s/', instance=debt)


@login_required
@require_POST
def debt_pay(request, pk):
    """Pay one instalment, or for money owed to you, record that they paid you back."""
    debt = get_object_or_404(Debt, pk=pk, user=request.user)
    amount = min(debt.monthly, debt.remaining)
    if amount > 0:
        debt.paid += amount
        debt.save()
        if debt.kind == 'receivable':
            Transaction.objects.create(user=request.user, kind='income', amount=amount, category='other',
                                       description=f'Paid back: {debt.name}', account=debt.account)
            messages.success(request, 'Settlement recorded.')
        else:
            Transaction.objects.create(user=request.user, kind='expense', amount=amount, category='bills',
                                       description=f'Payment: {debt.name}', account=debt.account)
            messages.success(request, 'Payment recorded.')
    return redirect(f'/explore/{debt.kind}s/')


@login_required
@require_POST
def debt_delete(request, pk):
    debt = get_object_or_404(Debt, pk=pk, user=request.user)
    return _delete(request, debt, f'/explore/{debt.kind}s/', 'Plan')
