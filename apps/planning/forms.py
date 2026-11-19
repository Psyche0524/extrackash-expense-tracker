from django import forms

from apps.core.forms import DATE, MONEY, UserForm, positive
from apps.planning.models import Budget, Contribution, Goal, PlannedPayment, Trip
from apps.transactions.forms import custom_categories
from apps.transactions.models import EXPENSE_CATEGORIES, INCOME_CATEGORIES


class BudgetForm(UserForm):
    class Meta:
        model = Budget
        fields = ['category', 'period', 'limit']
        widgets = {'limit': MONEY}

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.user = user
        self.fields['category'].widget = forms.Select(choices=EXPENSE_CATEGORIES + custom_categories(user, 'expense'))

    def clean_limit(self):
        return positive(self, 'limit')

    def clean_category(self):
        category = self.cleaned_data['category']
        taken = self.user.budgets.filter(category=category).exclude(pk=self.instance.pk)
        if taken.exists():
            raise forms.ValidationError('You already have a budget for this category.')
        return category


class GoalForm(UserForm):
    class Meta:
        model = Goal
        fields = ['name', 'note', 'target', 'target_date']
        widgets = {'target': MONEY, 'target_date': DATE}

    def clean_target(self):
        return positive(self, 'target')


class ContributionForm(UserForm):
    class Meta:
        model = Contribution
        fields = ['amount', 'description', 'date']
        widgets = {'amount': MONEY, 'date': DATE}

    def clean_amount(self):
        return positive(self, 'amount')


class PlannedPaymentForm(UserForm):
    class Meta:
        model = PlannedPayment
        fields = ['kind', 'name', 'amount', 'category', 'account', 'next_date', 'repeat']
        widgets = {'amount': MONEY, 'next_date': DATE}

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['category'].widget = forms.Select(choices=EXPENSE_CATEGORIES + INCOME_CATEGORIES[:-1])

    def clean_amount(self):
        return positive(self, 'amount')


class TripForm(UserForm):
    class Meta:
        model = Trip
        fields = ['name', 'start', 'end', 'budget']
        widgets = {'start': DATE, 'end': DATE, 'budget': MONEY}

    def clean(self):
        data = super().clean()
        if data.get('start') and data.get('end') and data['end'] < data['start']:
            self.add_error('end', 'End date must be after the start date.')
        return data
