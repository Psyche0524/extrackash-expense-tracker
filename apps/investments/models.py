from django.db import models

from apps.core.utils import MONEY, USER


class Investment(models.Model):
    user = models.ForeignKey(USER, on_delete=models.CASCADE, related_name='investments')
    name = models.CharField(max_length=60)
    label = models.CharField('Type', max_length=40, blank=True, help_text='e.g. Long-term, Fixed income')
    invested = models.DecimalField('Amount put in', **MONEY)
    value = models.DecimalField('Current value', **MONEY)
    updated = models.DateField(auto_now=True)

    class Meta:
        ordering = ['-value']
