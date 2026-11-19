from django.db import models

from apps.core.utils import MONEY, USER


class Household(models.Model):
    name = models.CharField(max_length=60)
    members = models.ManyToManyField(USER, related_name='households')
    shared_budget = models.DecimalField('Monthly shared budget', default=0, **MONEY)
