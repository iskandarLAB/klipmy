from django.contrib import admin
from .models import Campaign

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand_name', 'category', 'budget_total', 'budget_spent', 'rate_per_1k_views', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'category', 'target_platforms', 'is_featured')
    search_fields = ('title', 'brand_name', 'required_hashtags')
