from django.db import models
from django.conf import settings
from decimal import Decimal

class DepositPayment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Menunggu Bayaran'),
        ('paid', 'Berjaya Dibayar'),
        ('failed', 'Gagal'),
        ('cancelled', 'Dibatalkan'),
    )

    campaign = models.ForeignKey('campaigns.Campaign', on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='deposits')
    reference = models.CharField(max_length=64, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    chip_purchase_id = models.CharField(max_length=128, blank=True, null=True)
    checkout_url = models.URLField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    paid_at = models.DateTimeField(blank=True, null=True)
    raw_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} - RM{self.amount} ({self.get_status_display()})"
