from django.contrib import admin
from .models import PayoutRequest

@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ('reference', 'clipper', 'amount', 'method', 'recipient_name', 'status', 'created_at', 'paid_at')
    list_filter = ('status', 'method')
    search_fields = ('reference', 'clipper__username', 'recipient_name', 'duitnow_id', 'account_number')
