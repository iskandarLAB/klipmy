from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('clipper', 'Clipper (Creator)'),
        ('brand', 'Brand (Pengiklan)'),
        ('admin', 'Admin Platform'),
    )

    BANK_CHOICES = (
        ('maybank', 'Maybank'),
        ('cimb', 'CIMB Bank'),
        ('public', 'Public Bank'),
        ('rhb', 'RHB Bank'),
        ('hongleong', 'Hong Leong Bank'),
        ('ambank', 'AmBank'),
        ('bankislam', 'Bank Islam'),
        ('bsn', 'BSN'),
        ('tng', 'Touch n Go eWallet'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='clipper')
    phone = models.CharField(max_length=20, blank=True, null=True)
    tiktok_handle = models.CharField(max_length=100, blank=True, null=True, help_text="Contoh: @klippermy")
    instagram_handle = models.CharField(max_length=100, blank=True, null=True, help_text="Contoh: @klippermy")
    
    # Maklumat Payout (DuitNow / Bank)
    bank_name = models.CharField(max_length=50, choices=BANK_CHOICES, blank=True, null=True)
    bank_account_no = models.CharField(max_length=50, blank=True, null=True)
    duitnow_id = models.CharField(max_length=50, blank=True, null=True, help_text="No Telefon atau No KP untuk DuitNow")
    
    # Baki Wallet (RM)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    @property
    def is_clipper(self):
        return self.role == 'clipper'

    @property
    def is_brand(self):
        return self.role == 'brand'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
