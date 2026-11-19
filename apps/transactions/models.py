from django.db import models
from django.utils import timezone

from apps.core.utils import MONEY, USER, _now_time


EXPENSE_CATEGORIES = [
    ('dining', 'Food'),
    ('groceries', 'Groceries'),
    ('transport', 'Transport'),
    ('phone', 'Phone'),
    ('bills', 'Bills'),
    ('subscriptions', 'Subscriptions'),
    ('shopping', 'Shopping'),
    ('fun', 'Fun'),
    ('health', 'Health'),
    ('fees', 'Fees'),
    ('other', 'Other'),
]


INCOME_CATEGORIES = [
    ('salary', 'Salary'), ('bonus', 'Bonus'), ('freelance', 'Freelance'), ('commission', 'Commission'),
    ('business', 'Business'), ('side_hustle', 'Side hustle'), ('allowance', 'Allowance'), ('gift', 'Gift'),
    ('refund', 'Refund'), ('cashback', 'Cashback'), ('interest', 'Interest'), ('dividend', 'Dividend'),
    ('rental', 'Rental'), ('other', 'Other'),
]


CATEGORIES = EXPENSE_CATEGORIES + INCOME_CATEGORIES[:-1]


LABELS = dict(CATEGORIES)


def category_label(value):
    """Built-in categories have a nice label; custom ones are shown as typed."""
    return LABELS.get(value, value)


class Transaction(models.Model):
    EXPENSE = 'expense'
    INCOME = 'income'
    TRANSFER = 'transfer'
    KINDS = [(EXPENSE, 'Expense'), (INCOME, 'Income'), (TRANSFER, 'Transfer')]
    CATEGORIES = CATEGORIES

    user = models.ForeignKey(USER, on_delete=models.CASCADE, related_name='transactions')
    kind = models.CharField(max_length=10, choices=KINDS, default=EXPENSE)
    description = models.CharField('Merchant or description', max_length=100)
    amount = models.DecimalField(**MONEY)
    category = models.CharField(max_length=30, default='other')
    date = models.DateField(default=timezone.localdate)
    time = models.TimeField(default=_now_time)
    note = models.CharField(max_length=200, blank=True)
    tags = models.CharField(max_length=100, blank=True, help_text='Comma separated, e.g. japan, birthday')
    photo = models.FileField('Photo or receipt', upload_to='receipts/%Y/%m/', blank=True)
    # account is null for money coming in from outside; to_account is null for money going outside.
    account = models.ForeignKey('wallets.Account', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    to_account = models.ForeignKey('wallets.Account', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    shared = models.BooleanField('Shared with my household', default=False)

    class Meta:
        ordering = ['-date', '-time', '-id']

    def __str__(self):
        return f'{self.description} ({self.amount})'

    def get_category_display(self):
        return category_label(self.category)

    @property
    def tag_list(self):
        return [t.strip().lower() for t in self.tags.split(',') if t.strip()]
