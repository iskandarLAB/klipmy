from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal
from campaigns.models import Campaign
from .models import ClipSubmission
from .services import parse_video_url, update_submission_views

@login_required
def submit_clip_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)

    if campaign.status != 'active':
        messages.error(request, "Kempen ini tidak lagi menerima hantaran klip baharu.")
        return redirect('campaigns:detail', pk=campaign.id)

    if request.method == 'POST':
        video_url = request.POST.get('video_url', '').strip()

        if not video_url:
            messages.error(request, "Sila masukkan pautan (link) video TikTok atau Instagram Reel anda.")
            return redirect('campaigns:detail', pk=campaign.id)

        parsed = parse_video_url(video_url)
        if not parsed:
            messages.error(request, "Format pautan tidak sah. Sila pastikan anda memasukkan link TikTok atau Instagram Reels yang betul.")
            return redirect('campaigns:detail', pk=campaign.id)

        platform = parsed['platform']
        video_id = parsed['video_id']
        handle = parsed['handle']

        # Semak kesesuaian platform dengan kempen
        if campaign.target_platforms != 'both' and campaign.target_platforms != platform:
            messages.error(request, f"Kempen ini hanya menerima video daripada {campaign.get_target_platforms_display()}.")
            return redirect('campaigns:detail', pk=campaign.id)

        # Semak duplikasi video ID dalam kempen ini
        if ClipSubmission.objects.filter(campaign=campaign, video_id=video_id).exists():
            messages.warning(request, "Video ini telah pun didaftarkan sebelum ini dalam kempen ini.")
            return redirect('submissions:my_clips')

        # Cipta submission
        submission = ClipSubmission.objects.create(
            campaign=campaign,
            clipper=request.user,
            platform=platform,
            video_url=video_url,
            video_id=video_id,
            creator_handle=handle or request.user.tiktok_handle or request.user.username,
            status='approved'
        )

        # Jalankan tracking tontonan permulaan
        update_submission_views(submission)

        messages.success(
            request, 
            f"Tahniah! Klip {submission.get_platform_display()} anda berjaya dihantar. Sistem telah mula menjejak tontonan & menjana ganjaran!"
        )
        return redirect('submissions:my_clips')

    return redirect('campaigns:detail', pk=campaign.id)

@login_required
def my_clips_view(request):
    """Senarai video clipper beserta metrik live views dan RM terkumpul"""
    submissions = ClipSubmission.objects.filter(clipper=request.user).select_related('campaign')
    
    total_views = submissions.aggregate(Sum('verified_views'))['verified_views__sum'] or 0
    total_earned = submissions.aggregate(Sum('earnings'))['earnings__sum'] or Decimal('0.00')

    context = {
        'submissions': submissions,
        'total_views': total_views,
        'total_earned': total_earned,
    }
    return render(request, 'submissions/my_clips.html', context)

@login_required
def sync_clip_view(request, pk):
    """Kemas kini views bagi klip tertentu secara manual"""
    submission = get_object_or_404(ClipSubmission, pk=pk, clipper=request.user)
    update_submission_views(submission)
    messages.success(request, f"Views untuk video {submission.get_platform_display()} dikemaskini: {submission.verified_views:,} views (RM {submission.earnings})")
    return redirect('submissions:my_clips')

@login_required
def sync_all_views_view(request):
    """Kemas kini views untuk semua klip clipper ini"""
    submissions = ClipSubmission.objects.filter(clipper=request.user, status='approved')
    count = 0
    for sub in submissions:
        update_submission_views(sub)
        count += 1
    messages.success(request, f"Sebanyak {count} video berjaya disemak & dikemaskini tontonannya!")
    return redirect('submissions:my_clips')
