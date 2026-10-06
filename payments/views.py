import uuid
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.conf import settings

from campaigns.models import Campaign
from .models import DepositPayment
from .gateways.chip import ChipGateway
from .gateways import InvalidSignature, GatewayError

@login_required
def checkout_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id, brand=request.user)

    if campaign.status == 'active':
        messages.info(request, "Kempen ini telah pun aktif dan dibayar.")
        return redirect('campaigns:brand_dashboard')

    # Cari rekod bayaran sedia ada atau cipta baharu
    ref = f"DEP-{campaign.id}-{uuid.uuid4().hex[:6].upper()}"
    payment_record = DepositPayment.objects.create(
        campaign=campaign,
        user=request.user,
        reference=ref,
        amount=campaign.budget_total,
        status='pending'
    )

    gateway = ChipGateway()
    try:
        res = gateway.create_purchase(payment_record, request)
        checkout_url = res.get('checkout_url')
        if res.get('is_mock'):
            return redirect(checkout_url)
        return redirect(checkout_url)
    except GatewayError as e:
        messages.error(request, f"Gagal menghubungi gateway CHIP: {e}")
        return redirect('campaigns:brand_dashboard')

def mock_checkout_view(request, reference):
    """
    Antaramuka simulasi bayaran FPX CHIP untuk tujuan pembangunan & ujian tempatan
    apabila API key CHIP belum diletakkan dalam fail persekitaran (.env).
    """
    payment = get_object_or_404(DepositPayment, reference=reference)
    campaign = payment.campaign

    if request.method == 'POST':
        selected_bank = request.POST.get('bank', 'Maybank2u')
        # Luluskan bayaran
        payment.status = 'paid'
        payment.paid_at = timezone.now()
        payment.raw_response = f"Simulasi FPX berjaya melalui {selected_bank}"
        payment.save()

        # Aktifkan kempen
        campaign.status = 'active'
        campaign.save(update_fields=['status'])

        messages.success(request, f"Bayaran deposit bajet RM {payment.amount} melalui {selected_bank} (CHIP FPX) berjaya! Kempen anda kini aktif.")
        return redirect('payments:return_page')

    return render(request, 'payments/mock_checkout.html', {
        'payment': payment,
        'campaign': campaign,
    })

@csrf_exempt
def chip_callback_view(request):
    """Webhook panggilan balik (callback) daripada pelayan CHIP"""
    if request.method != 'POST':
        return HttpResponse("Kaedah tidak dibenarkan", status=405)

    signature = request.headers.get('X-Signature', '')
    raw_body = request.body
    gateway = ChipGateway()

    try:
        payload = gateway.verify_callback(raw_body, signature)
    except InvalidSignature as e:
        return HttpResponse(f"Tandatangan tidak sah: {e}", status=400)
    except Exception as e:
        return HttpResponse(f"Ralat: {e}", status=500)

    event_type = payload.get('event_type')
    purchase = payload.get('purchase', {})
    ref = purchase.get('reference')
    status = purchase.get('status')

    try:
        payment = DepositPayment.objects.get(reference=ref)
    except DepositPayment.DoesNotExist:
        return HttpResponse("Rekod tidak dijumpai", status=404)

    if status == 'paid' and payment.status != 'paid':
        payment.status = 'paid'
        payment.paid_at = timezone.now()
        payment.save()

        campaign = payment.campaign
        campaign.status = 'active'
        campaign.save(update_fields=['status'])

    return HttpResponse("OK", status=200)

def return_page_view(request):
    """Laman kembali selepas pembayaran di CHIP selesai"""
    ref = request.GET.get('ref')
    if ref:
        payment = DepositPayment.objects.filter(reference=ref).first()
        if payment and payment.status != 'paid':
            # Semak status terkini jika perlu
            payment.status = 'paid'
            payment.paid_at = timezone.now()
            payment.save()
            campaign = payment.campaign
            campaign.status = 'active'
            campaign.save(update_fields=['status'])
            messages.success(request, "Deposit kempen anda telah disahkan dan diaktifkan!")

    return render(request, 'payments/success.html')
