from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.core.utils import _available, _budget_rows, _delete, _form_page, _month_start, _set_user, _sum
from apps.planning.forms import BudgetForm, ContributionForm, GoalForm, PlannedPaymentForm, TripForm
from apps.planning.models import Budget, Goal, PlannedPayment, Trip
from apps.transactions.models import Transaction


@login_required
def plan(request):
    user = request.user
    debts = user.debts.all()
    return render(request, 'plan.html', {
        'budgets': user.budgets.count(), 'goals': user.goals.count(),
        'loans': debts.filter(kind='loan').count(), 'installments': debts.filter(kind='installment').count(),
        'receivables': debts.filter(kind='receivable').count(),
        'recurring': user.planned.filter(active=True).exclude(repeat='once').count(),
        'one_time': user.planned.filter(active=True, repeat='once').count(),
        'investments': user.investments.count(), 'trips': user.trips.count(),
        'tab': 'plan',
    })


@login_required
def budgets(request):
    rows = _budget_rows(request.user)
    total = sum(r['budget'].limit for r in rows)
    spent = sum(r['spent'] for r in rows)
    return render(request, 'budgets.html', {
        'rows': rows, 'total': total, 'spent': spent, 'left': total - spent,
        'pct': int(spent / total * 100) if total else 0, 'month': timezone.localdate(), 'tab': 'plan', 'sub': 'budgets',
    })


@login_required
def budget_detail(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    row = next(r for r in _budget_rows(request.user) if r['budget'] == budget)
    days_left = (row['end'] - timezone.localdate()).days
    recent = request.user.transactions.filter(kind='expense', category=budget.category,
                                              date__gte=row['start'], date__lt=row['end']).select_related('account')
    return render(request, 'budget.html', {
        **row, 'recent': recent, 'days_left': days_left, 'next_month': row['end'],
        'per_day': max(row['left'], 0) / days_left, 'tab': 'plan',
    })


@login_required
def planned(request):
    items = list(request.user.planned.filter(active=True).select_related('account'))
    return render(request, 'planned.html', {
        'items': items, 'month_total': sum(p.amount for p in items if p.kind == 'expense' and p.next_date < _add_month_start()),
        'tab': 'plan',
    })


def _add_month_start():
    return (_month_start() + timedelta(days=32)).replace(day=1)


@login_required
def planned_new(request):
    return _form_page(request, PlannedPaymentForm, 'Plan a payment', 'planned', on_save=_set_user(request),
                      initial={'kind': request.GET.get('kind', 'expense')})


@login_required
def planned_edit(request, pk):
    item = get_object_or_404(PlannedPayment, pk=pk, user=request.user)
    return _form_page(request, PlannedPaymentForm, 'Edit planned payment', 'planned', instance=item)


@login_required
@require_POST
def planned_done(request, pk):
    """Record this occurrence as a real transaction and move to the next due date."""
    item = get_object_or_404(PlannedPayment, pk=pk, user=request.user, active=True)
    Transaction.objects.create(user=request.user, kind=item.kind, amount=item.amount, category=item.category,
                               description=item.name, account=item.account)
    item.advance()
    item.save()
    messages.success(request, 'Payment recorded.')
    return redirect(request.POST.get('next') or 'planned')


@login_required
@require_POST
def planned_delete(request, pk):
    return _delete(request, get_object_or_404(PlannedPayment, pk=pk, user=request.user), 'planned', 'Planned payment')


@login_required
def trips(request):
    trip_list = list(request.user.trips.all())
    for t in trip_list:
        t.total = t.spent
        t.pct = int(t.total / t.budget * 100) if t.budget else 0
    return render(request, 'travel.html', {'trips': trip_list, 'tab': 'plan'})


@login_required
def trip_new(request):
    return _form_page(request, TripForm, 'Plan a trip', 'trips', on_save=_set_user(request),
                      subtitle='Spending between the start and end dates counts toward the trip.')


@login_required
def trip_edit(request, pk):
    trip = get_object_or_404(Trip, pk=pk, user=request.user)
    return _form_page(request, TripForm, 'Edit trip', 'trips', instance=trip)


@login_required
@require_POST
def trip_delete(request, pk):
    return _delete(request, get_object_or_404(Trip, pk=pk, user=request.user), 'trips', 'Trip')


@login_required
def tags(request):
    totals = {}
    for t in request.user.transactions.exclude(tags='').filter(kind='expense'):
        for tag in t.tag_list:
            row = totals.setdefault(tag, {'tag': tag, 'total': Decimal(0), 'count': 0})
            row['total'] += t.amount
            row['count'] += 1
    return render(request, 'tags.html', {
        'tags': sorted(totals.values(), key=lambda r: -r['total']), 'tab': 'plan',
    })


@login_required
def budget_new(request):
    return _form_page(request, BudgetForm, 'Create budget', 'plan', on_save=_set_user(request),
                      initial={'category': request.GET.get('category')})


@login_required
def budget_edit(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    return _form_page(request, BudgetForm, 'Edit budget', lambda b: f'/plan/budgets/{b.pk}/', instance=budget)


@login_required
@require_POST
def budget_delete(request, pk):
    return _delete(request, get_object_or_404(Budget, pk=pk, user=request.user), 'plan', 'Budget')


@login_required
def goals(request):
    goal_list = list(request.user.goals.all())
    return render(request, 'goals.html', {
        'goals': goal_list, 'total': sum(g.saved for g in goal_list), 'tab': 'plan', 'sub': 'goals',
    })


@login_required
def goal_detail(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    saved = goal.saved
    return render(request, 'goal.html', {
        'goal': goal, 'saved': saved, 'left': max(goal.target - saved, 0),
        'pct': min(int(saved / goal.target * 100), 100), 'tab': 'plan',
    })


@login_required
def goal_new(request):
    return _form_page(request, GoalForm, 'Create goal', 'goals', on_save=_set_user(request))


@login_required
def goal_edit(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    return _form_page(request, GoalForm, 'Edit goal', lambda g: f'/plan/goals/{g.pk}/', instance=goal)


@login_required
def goal_add_money(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    return _form_page(request, ContributionForm, f'Add to {goal.name}', f'/plan/goals/{goal.pk}/',
                      on_save=lambda c: setattr(c, 'goal', goal))


@login_required
@require_POST
def goal_delete(request, pk):
    return _delete(request, get_object_or_404(Goal, pk=pk, user=request.user), 'goals', 'Goal')


@login_required
def cashflow(request):
    user = request.user
    today = timezone.localdate()
    last_30 = user.transactions.filter(date__gt=today - timedelta(days=30))
    # shortcut: projects the last 30 days forward; add recurring transactions if users need exact forecasts.
    income = _sum(last_30.filter(kind='income'))
    spending = _sum(last_30.filter(kind='expense'))
    debts = [d for d in user.debts.all() if d.remaining > 0]
    commitments = sum(min(d.monthly, d.remaining) for d in debts)
    available = _available(user)
    return render(request, 'cashflow.html', {
        'available': available, 'income': income, 'spending': spending, 'commitments': commitments,
        'debt_count': len(debts), 'projected': available + income - spending - commitments,
        'until': today + timedelta(days=30), 'tab': 'plan', 'sub': 'cashflow',
    })
