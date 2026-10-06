from django.db import models
from django.conf import settings
from decimal import Decimal

class ClipSubmission(models.Model):
    PLATFORM_CHOICES = (
        ('tiktok', 'TikTok'),
        ('reels', 'Instagram Reels'),
    )

    STATUS_CHOICES = (
        ('pending', 'Menunggu Semakan'),
        ('approved', 'Disahkan & Sedang Ditjejak'),
        ('rejected', 'Ditolak (Tidak Ikut Syarat)'),
        ('completed', 'Selesai & Dikreditkan'),
    )

    campaign = models.ForeignKey('campaigns.Campaign', on_delete=models.CASCADE, related_name='submissions')
    clipper = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    video_url = models.URLField(max_length=500, help_text="Link penuh ke video TikTok atau Instagram Reel")
    video_id = models.CharField(max_length=150, help_text="ID unik video untuk elak duplikasi")
    creator_handle = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    
    # Metrik Views
    initial_views = models.PositiveIntegerField(default=0, help_text="Views semasa video mula dihantar")
    current_views = models.PositiveIntegerField(default=0, help_text="Views terkini dikesan sistem")
    verified_views = models.PositiveIntegerField(default=0, help_text="Jumlah views sah yang layak dibayar")
    
    # Kiraan Ganjaran
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Ganjaran terkumpul (RM)")
    paid_to_wallet = models.BooleanField(default=False, help_text="Adakah ganjaran sudah dipindahkan ke wallet clipper")

    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    last_checked_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('campaign', 'video_id')

    def __str__(self):
        return f"{self.clipper.username} - {self.platform} ({self.verified_views:,} views)"

    def calculate_earnings(self):
        """Kira ganjaran berdasarkan verified views x kadar kempen (dihadkan pada max payout per clip)"""
        rate = self.campaign.rate_per_1k_views
        max_cap = self.campaign.max_payout_per_clip
        calc = (Decimal(self.verified_views) / Decimal(1000)) * rate
        final_earnings = min(calc, max_cap)
        self.earnings = round(final_earnings, 2)
        return self.earnings


class ViewLog(models.Model):
    submission = models.ForeignKey(ClipSubmission, on_delete=models.CASCADE, related_name='view_logs')
    views = models.PositiveIntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
