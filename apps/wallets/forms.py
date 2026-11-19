from django import forms

from apps.core.forms import DATE, MONEY, PHOTO, TIME, UserForm, check_photo, positive
from apps.core.utils import _now_time
from apps.transactions.models import Transaction
from apps.wallets.models import Account


class TransferForm(UserForm):
    MODES = [('mine', 'My accounts'), ('external', 'Outside')]
    source = forms.ChoiceField(choices=MODES, initial='mine', required=False, widget=forms.RadioSelect)
    destination = forms.ChoiceField(choices=MODES, initial='mine', required=False, widget=forms.RadioSelect)
    fee = forms.DecimalField(label='Transfer fee (optional)', required=False, widget=MONEY)

    class Meta:
        model = Transaction
        fields = ['account', 'to_account', 'amount', 'date', 'time', 'note', 'photo']
        labels = {'account': 'From account', 'to_account': 'To account', 'note': 'Note (optional)'}
        widgets = {'date': DATE, 'time': TIME, 'amount': MONEY, 'photo': PHOTO}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['time'].required = False
        if self.instance.pk:
            self.initial.setdefault('source', 'mine' if self.instance.account_id else 'external')
            self.initial.setdefault('destination', 'mine' if self.instance.to_account_id else 'external')

    def clean_amount(self):
        return positive(self, 'amount')

    def clean_photo(self):
        return check_photo(self)

    def clean(self):
        data = super().clean()
        data['time'] = data.get('time') or _now_time()
        data['source'] = data.get('source') or 'mine'
        data['destination'] = data.get('destination') or 'mine'
        if data.get('source') == 'external':
            data['account'] = None
        elif not data.get('account'):
            self.add_error('account', 'Pick the account the money leaves.')
        if data.get('destination') == 'external':
            data['to_account'] = None
        elif not data.get('to_account'):
            self.add_error('to_account', 'Pick the account the money goes to.')
        if data.get('source') == data.get('destination') == 'external':
            raise forms.ValidationError('At least one side must be one of your accounts.')
        if data.get('account') and data.get('account') == data.get('to_account'):
            raise forms.ValidationError('Pick two different accounts.')
        fee = data.get('fee')
        if fee is not None and fee < 0:
            self.add_error('fee', 'Fee cannot be negative.')
        if fee and not data.get('account'):
            self.add_error('fee', 'Fees come out of one of your accounts.')
        return data


class AccountForm(UserForm):
    class Meta:
        model = Account
        fields = ['provider', 'name', 'kind', 'group', 'opening_balance', 'interest_rate', 'credit_limit', 'due_day']
        widgets = {'opening_balance': MONEY, 'credit_limit': MONEY}
        help_texts = {'name': 'Leave blank to use the wallet or bank name.'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False

    def clean(self):
        data = super().clean()
        if not data.get('name') and data.get('provider'):
            data['name'] = dict(self.fields['provider'].choices)[data['provider']]
        return data
