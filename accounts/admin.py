from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'wallet_balance', 'total_earned', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profil Clipper & Brand', {'fields': ('role', 'phone', 'tiktok_handle', 'instagram_handle')}),
        ('Maklumat Bank & Payout', {'fields': ('bank_name', 'bank_account_no', 'duitnow_id', 'wallet_balance', 'total_earned')}),
    )
