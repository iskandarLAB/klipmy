from django.db import models
from django.conf import settings
from decimal import Decimal

class PayoutRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Menunggu Kelulusan'),
        ('processing', 'Sedang Diproses'),
        ('completed', 'Berjaya Dipindahkan'),
        ('rejected', 'Ditolak'),
    )

    METHOD_CHOICES = (
        ('duitnow', 'DuitNow ID (No Phone / No KP)'),
        ('bank', 'Pindahan Bank Tempatan (Maybank, CIMB, dll)'),
    )

    clipper = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payouts')
    reference = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='duitnow')
    
    # Maklumat Penerima
    recipient_name = models.CharField(max_length=150)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    duitnow_id = models.CharField(max_length=50, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - {self.clipper.username} (RM {self.amount})"
