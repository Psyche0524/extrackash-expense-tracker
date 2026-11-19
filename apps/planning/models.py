from datetime import date, timedelta

from django.db import models
from django.utils import timezone

from apps.core.utils import MONEY, USER, _add_months, _sum
from apps.transactions.models import Transaction, category_label


class Budget(models.Model):
    PERIODS = [('daily', 'Daily'), ('weekly', 'Weekly'), ('biweekly', 'Every 2 weeks'), ('monthly', 'Monthly'), ('yearly', 'Yearly')]

    user = models.ForeignKey(USER, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=30)
    period = models.CharField(max_length=10, choices=PERIODS, default='monthly')
    limit = models.DecimalField(**MONEY)

    class Meta:
        ordering = ['category']
        constraints = [models.UniqueConstraint(fields=['user', 'category'], name='one_budget_per_category')]

    def get_category_display(self):
        return category_label(self.category)

    def window(self, today):
        """(start, next_start) of the budget period that contains today."""
        if self.period == 'daily':
            return today, today + timedelta(days=1)
        if self.period in ('weekly', 'biweekly'):
            days = 7 if self.period == 'weekly' else 14
            # bi-weekly periods count from a fixed Monday so they don't drift
            start = today - timedelta(days=(today - date(2024, 1, 1)).days % days)
            return start, start + timedelta(days=days)
        if self.period == 'yearly':
            return today.replace(month=1, day=1), today.replace(year=today.year + 1, month=1, day=1)
        start = today.replace(day=1)
        return start, (start + timedelta(days=32)).replace(day=1)


class Goal(models.Model):
    user = models.ForeignKey(USER, on_delete=models.CASCADE, related_name='goals')
    name = models.CharField(max_length=60)
    note = models.CharField(max_length=100, blank=True)
    target = models.DecimalField(**MONEY)
    target_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['id']

    @property
    def saved(self):
        return _sum(self.contributions.all())


class Contribution(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='contributions')
    description = models.CharField(max_length=60, default='Contribution')
    amount = models.DecimalField(**MONEY)
    date = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['-date', '-id']


class PlannedPayment(models.Model):
    """A bill or income you expect: once, or repeating."""
    REPEATS = [('once', 'One time'), ('weekly', 'Every week'), ('monthly', 'Every month'), ('yearly', 'Every year')]

    user = models.ForeignKey(USER, on_delete=models.CASCADE, related_name='planned')
    kind = models.CharField(max_length=10, choices=Transaction.KINDS[:2], default='expense')
    name = models.CharField(max_length=60)
    amount = models.DecimalField(**MONEY)
    category = models.CharField(max_length=30, default='bills')
    account = models.ForeignKey('wallets.Account', null=True, blank=True, on_delete=models.SET_NULL)
    next_date = models.DateField('Next due', default=timezone.localdate)
    repeat = models.CharField(max_length=10, choices=REPEATS, default='monthly')
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['next_date']

    def advance(self):
        """Move to the next due date, or switch off a one-time payment."""
        d = self.next_date
        if self.repeat == 'once':
            self.active = False
        elif self.repeat == 'weekly':
            self.next_date = d + timedelta(days=7)
        elif self.repeat == 'yearly':
            self.next_date = _add_months(d, 12)
        else:
            self.next_date = _add_months(d, 1)

    def dates_until(self, end):
        """Every due date from next_date up to end (for forecasts)."""
        out, probe = [], PlannedPayment(next_date=self.next_date, repeat=self.repeat)
        while self.active and probe.next_date <= end:
            out.append(probe.next_date)
            if probe.repeat == 'once':
                break
            probe.advance()
        return out


class Trip(models.Model):
    user = models.ForeignKey(USER, on_delete=models.CASCADE, related_name='trips')
    name = models.CharField(max_length=60)
    start = models.DateField()
    end = models.DateField()
    budget = models.DecimalField(default=0, **MONEY)

    class Meta:
        ordering = ['-start']

    @property
    def spent(self):
        return _sum(self.user.transactions.filter(kind='expense', date__range=(self.start, self.end)))
