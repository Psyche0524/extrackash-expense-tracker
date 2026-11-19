from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from apps.core.utils import _daily_bars, _insight, _month_start, _sum


def _greeting(hour):
    if hour < 12:
        return 'morning'
    return 'afternoon' if hour < 18 else 'evening'


def _forecast(user, months):
    """Expected bills and income per month from planned payments."""
    start = _month_start()
    planned = list(user.planned.filter(active=True))
    rows, m = [], start
    for _ in range(months):
        nxt = (m + timedelta(days=32)).replace(day=1)
        bills = income = Decimal(0)
        for p in planned:
            hits = [d for d in p.dates_until(nxt - timedelta(days=1)) if d >= m]
            if p.kind == 'income':
                income += p.amount * len(hits)
            else:
                bills += p.amount * len(hits)
        rows.append({'month': m, 'bills': bills, 'income': income, 'net': income - bills})
        m = nxt
    return rows


@login_required
def home(request):
    user = request.user
    today = timezone.localdate()
    span = request.GET.get('span', 'day')
    since = {'week': today - timedelta(days=today.weekday()), 'month': _month_start()}.get(span, today)
    period = user.transactions.filter(date__gte=since)
    week = [(d.strftime('%a')[0], _sum(user.transactions.filter(kind='expense', date=d)))
            for d in (today - timedelta(days=i) for i in range(6, -1, -1))]
    due = [p for p in user.planned.filter(active=True, kind='expense').select_related('account')
           if p.next_date <= today + timedelta(days=31)]
    for p in due:
        p.days_left = (p.next_date - today).days
    years = {'3y': 3, '5y': 5}.get(request.GET.get('forecast'), 1)
    return render(request, 'dashboard/home.html', {
        'today': today, 'insight': _insight(user),
        'greeting': _greeting(timezone.localtime().hour),
        'span': span, 'span_in': _sum(period.filter(kind='income')), 'span_out': _sum(period.filter(kind='expense')),
        'week': _daily_bars(week), 'due': due, 'due_total': sum(p.amount for p in due),
        'forecast': _forecast(user, 12 * years), 'years': years,
        'recent': user.transactions.select_related('account')[:5],
        'tab': 'home',
    })
