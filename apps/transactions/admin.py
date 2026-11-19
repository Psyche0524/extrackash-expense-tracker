from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'user', 'kind', 'description', 'category', 'amount']
    list_filter = ['kind', 'category']
    search_fields = ['description', 'note']
