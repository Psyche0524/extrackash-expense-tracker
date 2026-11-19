from django.contrib import admin

from .models import Budget, Contribution, Goal, PlannedPayment, Trip

admin.site.register([Budget, Goal, Contribution, PlannedPayment, Trip])
