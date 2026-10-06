from django.db import models
from django.conf import settings
from decimal import Decimal

class Campaign(models.Model):
    STATUS_CHOICES = (
        ('pending_payment', 'Menunggu Bayaran Deposit'),
        ('active', 'Sedang Berjalan (Aktif)'),
        ('paused', 'Dijeda (Paused)'),
        ('completed', 'Tamat (Bajet Penuh)'),
    )

    CATEGORY_CHOICES = (
        ('podcast', '🎙️ Podcast & Wawancara'),
        ('ecommerce', '🛍️ E-Commerce & Produk'),
        ('education', '📚 Edukasi & Bisnes'),
        ('lifestyle', '✨ Gaya Hidup & Hiburan'),
        ('fnb', '🍔 Makanan & Minuman (F&B)'),
        ('other', '📌 Lain-lain'),
    )

    PLATFORM_CHOICES = (
        ('both', 'TikTok & Instagram Reels'),
        ('tiktok', 'TikTok Sahaja'),
        ('reels', 'Instagram Reels Sahaja'),
    )

    brand = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaigns')
    title = models.CharField(max_length=200, help_text="Tajuk Kempen")
    brand_name = models.CharField(max_length=100, help_text="Nama Jenama / Syarikat")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='podcast')
    description = models.TextField(help_text="Ringkasan tentang kempen ini")
    
    # Bahan Mentah & Syarat
    raw_video_url = models.URLField(max_length=500, help_text="Pautan Google Drive / YouTube ke video asal")
    target_platforms = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='both')
    required_hashtags = models.CharField(max_length=255, help_text="Contoh: #JenamaAnda #KlipViral")
    guidelines = models.TextField(
        blank=True,
        default="1. Pastikan video sekurang-kurangnya 15 saat.\n2. Wajib letak hashtag yang ditetapkan di kapsyen.\n3. Jangan guna bot tontonan palsu (auto reject)."
    )

    # Struktur Bajet (RM)
    budget_total = models.DecimalField(max_digits=10, decimal_places=2, help_text="Jumlah Pool Bajet (RM)")
    budget_spent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Bajet Terpakai (RM)")
    rate_per_1k_views = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('10.00'), help_text="Kadar per 1,000 views (RM)")
    max_payout_per_clip = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('100.00'), help_text="Had maksimum bayaran bagi setiap video (RM)")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.brand_name})"

    @property
    def budget_remaining(self):
        return max(Decimal('0.00'), self.budget_total - self.budget_spent)

    @property
    def progress_percentage(self):
        if self.budget_total <= 0:
            return 0
        pct = (self.budget_spent / self.budget_total) * 100
        return min(100, int(pct))

    @property
    def total_views_generated(self):
        return sum(sub.verified_views for sub in self.submissions.filter(status='approved'))
