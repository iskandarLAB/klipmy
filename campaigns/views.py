from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from decimal import Decimal
from .models import Campaign
from submissions.models import ClipSubmission

def index_view(request):
    """Laman Utama / Terokai Kempen Clipping"""
    platform_filter = request.GET.get('platform', 'all')
    category_filter = request.GET.get('category', 'all')

    campaigns = Campaign.objects.filter(status='active')

    if platform_filter in ['tiktok', 'reels']:
        campaigns = campaigns.filter(Q(target_platforms='both') | Q(target_platforms=platform_filter))

    if category_filter != 'all':
        campaigns = campaigns.filter(category=category_filter)

    # Statistik Keseluruhan Platform
    total_paid_out = ClipSubmission.objects.filter(status='approved').aggregate(Sum('earnings'))['earnings__sum'] or Decimal('0.00')
    total_views = sum(c.total_views_generated for c in Campaign.objects.all())
    active_campaigns_count = Campaign.objects.filter(status='active').count()

    context = {
        'campaigns': campaigns,
        'selected_platform': platform_filter,
        'selected_category': category_filter,
        'categories': Campaign.CATEGORY_CHOICES,
        'total_paid_out': total_paid_out,
        'total_views': total_views,
        'active_campaigns_count': active_campaigns_count,
    }
    return render(request, 'campaigns/index.html', context)

def detail_view(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    submissions = campaign.submissions.filter(status='approved').order_by('-verified_views')[:10]
    
    # Semak jika user ini dah pernah submit
    user_submission = None
    if request.user.is_authenticated:
        user_submission = campaign.submissions.filter(clipper=request.user).first()

    context = {
        'campaign': campaign,
        'submissions': submissions,
        'user_submission': user_submission,
    }
    return render(request, 'campaigns/detail.html', context)

@login_required
def create_view(request):
    """Borang Lancar Kempen Baharu untuk Brand"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        brand_name = request.POST.get('brand_name', '').strip()
        category = request.POST.get('category', 'podcast')
        description = request.POST.get('description', '').strip()
        raw_video_url = request.POST.get('raw_video_url', '').strip()
        target_platforms = request.POST.get('target_platforms', 'both')
        required_hashtags = request.POST.get('required_hashtags', '').strip()
        guidelines = request.POST.get('guidelines', '').strip()

        try:
            budget_total = Decimal(request.POST.get('budget_total', '500.00'))
            rate_per_1k_views = Decimal(request.POST.get('rate_per_1k_views', '10.00'))
            max_payout_per_clip = Decimal(request.POST.get('max_payout_per_clip', '100.00'))
        except (ValueError, TypeError):
            messages.error(request, "Sila masukkan format angka bajet yang sah.")
            return render(request, 'campaigns/create.html', {'categories': Campaign.CATEGORY_CHOICES})

        if budget_total < 50:
            messages.error(request, "Bajet minima untuk melancarkan kempen adalah RM 50.00.")
            return render(request, 'campaigns/create.html', {'categories': Campaign.CATEGORY_CHOICES})

        campaign = Campaign.objects.create(
            brand=request.user,
            title=title,
            brand_name=brand_name,
            category=category,
            description=description,
            raw_video_url=raw_video_url,
            target_platforms=target_platforms,
            required_hashtags=required_hashtags,
            guidelines=guidelines,
            budget_total=budget_total,
            rate_per_1k_views=rate_per_1k_views,
            max_payout_per_clip=max_payout_per_clip,
            status='pending_payment',
        )

        messages.success(request, "Kempen berjaya dicipta! Sila buat bayaran deposit bajet untuk mengaktifkannya.")
        return redirect('payments:checkout', campaign_id=campaign.id)

    return render(request, 'campaigns/create.html', {'categories': Campaign.CATEGORY_CHOICES})

@login_required
def brand_dashboard_view(request):
    """Dashboard Pantau Prestasi untuk Brand"""
    my_campaigns = Campaign.objects.filter(brand=request.user).order_by('-created_at')
    
    total_budget = my_campaigns.aggregate(Sum('budget_total'))['budget_total__sum'] or Decimal('0.00')
    total_spent = my_campaigns.aggregate(Sum('budget_spent'))['budget_spent__sum'] or Decimal('0.00')
    
    total_clips = ClipSubmission.objects.filter(campaign__brand=request.user).count()
    total_views = sum(c.total_views_generated for c in my_campaigns)

    context = {
        'campaigns': my_campaigns,
        'total_budget': total_budget,
        'total_spent': total_spent,
        'total_clips': total_clips,
        'total_views': total_views,
    }
    return render(request, 'campaigns/brand_dashboard.html', context)

@login_required
def toggle_status_view(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, brand=request.user)
    if campaign.status == 'active':
        campaign.status = 'paused'
        messages.info(request, f"Kempen '{campaign.title}' telah dijeda.")
    elif campaign.status == 'paused':
        campaign.status = 'active'
        messages.success(request, f"Kempen '{campaign.title}' kini aktif semula.")
    campaign.save(update_fields=['status'])
    return redirect('campaigns:brand_dashboard')
