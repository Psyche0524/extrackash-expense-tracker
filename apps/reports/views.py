import csv
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from apps.core.utils import _month_start, _prev_month, _sum
from apps.transactions.models import category_label


@login_required
def reports(request):
    period = request.GET.get('period', 'month')
    today = timezone.localdate()
    if period == 'week':
        start = today - timedelta(days=today.weekday())
        prev_start = start - timedelta(days=7)
    elif period == 'year':
        start = today.replace(month=1, day=1)
        prev_start = start.replace(year=start.year - 1)
    else:
        period = 'month'
        start = _month_start()
        prev_start = _prev_month(start)
    expenses = request.user.transactions.filter(kind='expense')
    spent = _sum(expenses.filter(date__gte=start))
    prev = _sum(expenses.filter(date__gte=prev_start, date__lte=prev_start + (today - start)))

    by_cat = expenses.filter(date__gte=start).values('category').annotate(total=Sum('amount')).order_by('-total')
    top = by_cat[0]['total'] if by_cat else 1
    cats = [{'label': category_label(c['category']), 'total': c['total'], 'pct': int(c['total'] / top * 100)} for c in by_cat]

    months, m = [], _month_start()
    for _ in range(6):
        nxt = (m.replace(day=28) + timedelta(days=4)).replace(day=1)
        months.append({'month': m, 'total': _sum(expenses.filter(date__gte=m, date__lt=nxt))})
        m = _prev_month(m)
    months.reverse()
    peak = max(x['total'] for x in months) or 1
    for x in months:
        x['pct'] = int(x['total'] / peak * 100)

    return render(request, 'reports.html', {
        'period': period, 'start': start, 'spent': spent, 'diff': prev - spent, 'cats': cats, 'months': months, 'tab': 'plan',
    })


@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="extrackash-transactions.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Description', 'Category', 'Account', 'To account', 'Amount', 'Note'])
    for t in request.user.transactions.select_related('account', 'to_account').order_by('date', 'id'):
        writer.writerow([t.date, t.kind, t.description, t.get_category_display(), t.account or '', t.to_account or '', t.amount, t.note])
    return response
