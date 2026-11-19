from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core.utils import _month_start, _sum
from apps.households.forms import HouseholdForm, InviteForm
from apps.households.models import Household
from apps.transactions.models import Transaction


@login_required
def shared(request):
    home = request.user.households.prefetch_related('members').first()
    if not home:
        return render(request, 'shared.html', {'tab': 'plan'})
    members = list(home.members.all())
    shared_tx = Transaction.objects.filter(user__in=members, shared=True, kind='expense', date__gte=_month_start())
    total = _sum(shared_tx)
    share = total / len(members)
    people = [{'user': m, 'paid': _sum(shared_tx.filter(user=m))} for m in members]
    for p in people:
        p['balance'] = p['paid'] - share  # + means others owe them
    return render(request, 'shared.html', {
        'home': home, 'members': members, 'people': people, 'total': total, 'share': share,
        'left': home.shared_budget - total, 'pct': int(total / home.shared_budget * 100) if home.shared_budget else 0,
        'tab': 'plan',
    })


@login_required
def household_new(request):
    form = HouseholdForm(request.user, request.POST or None)
    if form.is_valid():
        home = form.save()
        home.members.add(request.user)
        messages.success(request, 'Household created.')
        return redirect('shared')
    return render(request, 'form.html', {'form': form, 'title': 'Create household', 'subtitle': 'Share spending with people you live with.'})


@login_required
def household_invite(request):
    home = get_object_or_404(Household, members=request.user)
    form = InviteForm(request.POST or None)
    if form.is_valid():
        home.members.add(form.cleaned_data['email'])
        messages.success(request, 'Member added.')
        return redirect('shared')
    return render(request, 'form.html', {'form': form, 'title': 'Invite member', 'subtitle': 'Shared spaces show your name and shared expenses only.'})


@login_required
@require_POST
def household_leave(request):
    home = get_object_or_404(Household, members=request.user)
    home.members.remove(request.user)
    if not home.members.exists():
        home.delete()
    messages.success(request, 'You left the household.')
    return redirect('shared')
