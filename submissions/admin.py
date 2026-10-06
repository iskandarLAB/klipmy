from django.contrib import admin
from .models import ClipSubmission, ViewLog

@admin.register(ClipSubmission)
class ClipSubmissionAdmin(admin.ModelAdmin):
    list_display = ('clipper', 'campaign', 'platform', 'verified_views', 'earnings', 'status', 'created_at')
    list_filter = ('status', 'platform', 'campaign')
    search_fields = ('clipper__username', 'video_url', 'creator_handle', 'video_id')

@admin.register(ViewLog)
class ViewLogAdmin(admin.ModelAdmin):
    list_display = ('submission', 'views', 'recorded_at')
