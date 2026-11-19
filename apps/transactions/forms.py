from django import forms

from apps.core.forms import DATE, MONEY, PHOTO, TIME, UserForm, check_photo
from apps.core.utils import _now_time
from apps.transactions.models import EXPENSE_CATEGORIES, INCOME_CATEGORIES, LABELS, Transaction, category_label


def custom_categories(user, kind):
    """Categories this user typed in before, so they show up as chips next time."""
    built_in = {v for v, _ in (EXPENSE_CATEGORIES if kind == 'expense' else INCOME_CATEGORIES)}
    used = user.transactions.filter(kind=kind).values_list('category', flat=True).distinct()
    return [(c, c) for c in used if c not in built_in and c not in LABELS]


class TransactionForm(UserForm):
    new_category = forms.CharField(label='New category', max_length=30, required=False,
                                   widget=forms.TextInput(attrs={'placeholder': '+ Add your own category'}))
    recurring = forms.BooleanField(label='Repeat every month', required=False)
    owed_by = forms.CharField(label='Someone owes me part of this', max_length=60, required=False,
                              widget=forms.TextInput(attrs={'placeholder': 'Their name'}))
    owed_amount = forms.DecimalField(label='How much they owe', required=False, widget=MONEY)

    class Meta:
        model = Transaction
        fields = ['kind', 'amount', 'category', 'description', 'account', 'date', 'time', 'note', 'tags', 'photo', 'shared']
        labels = {'description': 'Name (optional)'}
        widgets = {'kind': forms.RadioSelect, 'date': DATE, 'time': TIME, 'photo': PHOTO,
                   'amount': forms.TextInput(attrs={'inputmode': 'decimal', 'placeholder': '0', 'autocomplete': 'off'}),
                   'note': forms.TextInput(attrs={'placeholder': 'Add a note…'})}

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['kind'].choices = Transaction.KINDS[:2]  # transfers have their own form
        self.fields['account'].required = True
        self.fields['description'].required = False
        self.fields['category'].required = False
        self.fields['time'].required = False
        self.expense_categories = EXPENSE_CATEGORIES + custom_categories(user, 'expense')
        self.income_categories = INCOME_CATEGORIES + custom_categories(user, 'income')
        if not user.households.exists():
            del self.fields['shared']
        if self.instance.pk:  # editing: these only make sense when adding
            for name in ('recurring', 'owed_by', 'owed_amount'):
                del self.fields[name]

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError('Amount must be more than 0.')
        return amount

    def clean_photo(self):
        return check_photo(self)

    def clean(self):
        data = super().clean()
        data['time'] = data.get('time') or _now_time()
        data['category'] = (data.get('new_category') or '').strip() or data.get('category') or 'other'
        if not data.get('description'):
            data['description'] = category_label(data['category'])
        owed = data.get('owed_amount')
        if owed is not None and (owed <= 0 or (data.get('amount') and owed > data['amount'])):
            self.add_error('owed_amount', 'Must be more than 0 and not more than the amount.')
        if owed and not data.get('owed_by'):
            self.add_error('owed_by', 'Who owes you?')
        return data
