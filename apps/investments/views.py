from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from apps.core.utils import _delete, _form_page, _set_user
from apps.investments.forms import InvestmentForm
from apps.investments.models import Investment


@login_required
def investments(request):
    items = list(request.user.investments.all())
    value = sum(i.value for i in items)
    invested = sum(i.invested for i in items)
    for i in items:
        i.share = int(i.value / value * 100) if value else 0
    return render(request, 'investments.html', {
        'items': items, 'value': value, 'gain': value - invested,
        'gain_pct': round((value - invested) / invested * 100, 2) if invested else 0, 'tab': 'plan',
    })


@login_required
def investment_new(request):
    return _form_page(request, InvestmentForm, 'Add holding', 'investments', on_save=_set_user(request))


@login_required
def investment_edit(request, pk):
    item = get_object_or_404(Investment, pk=pk, user=request.user)
    return _form_page(request, InvestmentForm, 'Update investment', 'investments', instance=item)


@login_required
@require_POST
def investment_delete(request, pk):
    return _delete(request, get_object_or_404(Investment, pk=pk, user=request.user), 'investments', 'Holding')
