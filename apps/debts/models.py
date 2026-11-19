from django.db import models

from apps.core.utils import MONEY, USER


class Debt(models.Model):
    """Installments, loans and money owed to you: all are 'X a month until Y is paid'."""
    KINDS = [('installment', 'Installment'), ('loan', 'Loan'), ('receivable', 'Money owed to me')]

    user = models.ForeignKey(USER, on_delete=models.CASCADE, related_name='debts')
    kind = models.CharField(max_length=12, choices=KINDS, default='installment')
    name = models.CharField(max_length=60)
    total = models.DecimalField('Total amount', **MONEY)
    monthly = models.DecimalField('Monthly payment', **MONEY)
    paid = models.DecimalField('Already paid', default=0, **MONEY)
    account = models.ForeignKey('wallets.Account', null=True, blank=True, on_delete=models.SET_NULL, help_text='Where payments come from.')
    due_day = models.PositiveSmallIntegerField(null=True, blank=True)
    note = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['id']

    @property
    def remaining(self):
        return max(self.total - self.paid, 0)

    @property
    def payments_left(self):
        return -(-self.remaining // self.monthly) if self.monthly else 0
