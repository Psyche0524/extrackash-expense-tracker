from apps.core.forms import MONEY, UserForm, positive
from apps.debts.models import Debt


class DebtForm(UserForm):
    class Meta:
        model = Debt
        fields = ['kind', 'name', 'total', 'monthly', 'paid', 'account', 'due_day', 'note']
        widgets = {'total': MONEY, 'monthly': MONEY, 'paid': MONEY}

    def clean_total(self):
        return positive(self, 'total')

    def clean_monthly(self):
        return positive(self, 'monthly')
