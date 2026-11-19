from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone


USER = settings.AUTH_USER_MODEL


MONEY = {'max_digits': 12, 'decimal_places': 2}


def _now_time():
    return timezone.localtime().time().replace(second=0, microsecond=0)


def _add_months(d, n):
    month = d.month - 1 + n
    year, month = d.year + month // 12, month % 12 + 1
    # clamp e.g. Jan 31 + 1 month to Feb 28/29
    for day in (d.day, 30, 29, 28):
        try:
            return d.replace(year=year, month=month, day=day)
        except ValueError:
            continue


def _sum(qs):
    return qs.aggregate(t=Sum('amount'))['t'] or Decimal(0)


def _month_start(day=None):
    return (day or timezone.localdate()).replace(day=1)


def _prev_month(day):
    return (day - timedelta(days=1)).replace(day=1)


def _available(user):
    """Net worth: every account's balance added up (credit cards count as negative)."""
    return sum((a.balance for a in user.accounts.all()), Decimal(0))


def _budget_rows(user):
    today = timezone.localdate()
    rows = []
    for b in user.budgets.all():
        start, end = b.window(today)
        spent = _sum(user.transactions.filter(kind='expense', category=b.category, date__gte=start, date__lt=end))
        rows.append({'budget': b, 'spent': spent, 'left': b.limit - spent, 'pct': int(spent / b.limit * 100),
                     'start': start, 'end': end})
    return rows


def _daily_bars(values):
    """[(label, value)] -> rows with a 0-100 height for simple CSS bar charts."""
    peak = max((abs(v) for _, v in values), default=0) or 1
    return [{'label': label, 'value': v, 'pct': int(abs(v) / peak * 100)} for label, v in values]


def _insight(user):
    """One friendly sentence about this month, like the mascot tip in the recording."""
    month = user.transactions.filter(date__gte=_month_start())
    income, spent = _sum(month.filter(kind='income')), _sum(month.filter(kind='expense'))
    if not month.exists():
        return 'Log your first expense or income today to start seeing your patterns.'
    if spent > income:
        return "You've spent more than the income you've logged this month. Check your balances and any income you haven't logged."
    over = [r for r in _budget_rows(user) if r['left'] < 0]
    if over:
        return f"You're over your {over[0]['budget'].get_category_display()} budget. A slower few days will even it out."
    return f"You've kept {income - spent:,.0f} pesos of this month's income. That's money with room to grow."


def _form_page(request, form_class, title, done, instance=None, subtitle='', initial=None, on_save=None):
    """One page for every add/edit form. `on_save(obj)` fills fields the form doesn't show."""
    form = form_class(request.user, request.POST or None, request.FILES or None, instance=instance, initial=initial)
    if form.is_valid():
        obj = form.save(commit=False)
        if on_save:
            on_save(obj)
        obj.save()
        form.save_m2m()
        messages.success(request, 'Saved.')
        return redirect(done(obj) if callable(done) else done)
    return render(request, 'form.html', {'form': form, 'title': title, 'subtitle': subtitle, 'back': request.GET.get('back', '')})


def _delete(request, obj, done, label):
    obj.delete()
    messages.success(request, f'{label} removed.')
    return redirect(done)


def _set_user(request):
    return lambda obj: setattr(obj, 'user', request.user)
