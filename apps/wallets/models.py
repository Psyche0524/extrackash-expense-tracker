from django.db import models

from apps.core.utils import MONEY, USER, _sum
from apps.transactions.models import Transaction


class Account(models.Model):
    KINDS = [('bank', 'Bank'), ('wallet', 'E-wallet'), ('cash', 'Cash'), ('credit', 'Credit card')]
    # (value, label, card colour). Colours approximate each brand; logos are initials, not brand artwork.
    PROVIDERS = [
        ('gcash', 'GCash', '#1d4ed8'),
        ('maya', 'Maya', '#047857'),
        ('maribank', 'Maribank', '#ea580c'),
        ('gotyme', 'GoTyme', '#0e7490'),
        ('shopeepay', 'ShopeePay', '#dc2626'),
        ('coins', 'Coins.ph', '#2563eb'),
        ('bpi', 'BPI', '#b91c1c'),
        ('bdo', 'BDO', '#1e3a8a'),
        ('metrobank', 'Metrobank', '#1e40af'),
        ('unionbank', 'UnionBank', '#c2410c'),
        ('landbank', 'Landbank', '#15803d'),
        ('seabank', 'SeaBank', '#c2410c'),
        ('cash', 'Cash / Wallet', '#a16207'),
        ('other', 'Other', '#1e5f43'),
    ]
    COLORS = {value: color for value, _, color in PROVIDERS}

    user = models.ForeignKey(USER, on_delete=models.CASCADE, related_name='accounts')
    provider = models.CharField('Wallet or bank', max_length=12, choices=[(v, label) for v, label, _ in PROVIDERS], default='other')
    name = models.CharField(max_length=60)
    kind = models.CharField(max_length=10, choices=KINDS, default='bank')
    opening_balance = models.DecimalField('Current balance', default=0, help_text='For a credit card, enter what you owe as a negative number.', **MONEY)
    credit_limit = models.DecimalField(null=True, blank=True, help_text='Credit cards only.', **MONEY)
    due_day = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Credit cards only: day of the month the bill is due.')
    group = models.CharField(max_length=40, blank=True, help_text='Optional folder, e.g. "Savings" or "GO TRADE".')
    interest_rate = models.DecimalField('Interest rate (% a year)', max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name

    @property
    def is_liability(self):
        return self.kind == 'credit'

    @property
    def color(self):
        return self.COLORS.get(self.provider, '#1e5f43')

    @property
    def balance(self):
        # shortcut: 4 queries per account, fine for a handful of accounts; annotate if lists get long.
        tx = Transaction.objects
        return (self.opening_balance
                + _sum(tx.filter(account=self, kind='income'))
                - _sum(tx.filter(account=self, kind='expense'))
                - _sum(tx.filter(account=self, kind='transfer'))
                + _sum(tx.filter(to_account=self, kind='transfer')))
