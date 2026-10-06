from django.contrib import admin
from .models import DepositPayment

@admin.register(DepositPayment)
class DepositPaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'campaign', 'user', 'amount', 'status', 'created_at', 'paid_at')
    list_filter = ('status',)
    search_fields = ('reference', 'campaign__title', 'user__username', 'chip_purchase_id')
