from apps.core.forms import MONEY, UserForm
from apps.investments.models import Investment


class InvestmentForm(UserForm):
    class Meta:
        model = Investment
        fields = ['name', 'label', 'invested', 'value']
        widgets = {'invested': MONEY, 'value': MONEY}
