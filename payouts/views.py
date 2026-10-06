import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from .models import PayoutRequest

@login_required
def wallet_view(request):
    user = request.user
    payout_history = PayoutRequest.objects.filter(clipper=user).order_by('-created_at')

    min_withdrawal = Decimal(str(getattr(settings, 'MIN_WITHDRAWAL_AMOUNT', 20.00)))

    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0.00'))
        except (ValueError, TypeError):
            messages.error(request, "Format jumlah pengeluaran tidak sah.")
            return redirect('payouts:wallet')

        method = request.POST.get('method', 'duitnow')
        recipient_name = request.POST.get('recipient_name', '').strip()
        bank_name = request.POST.get('bank_name', '').strip()
        account_number = request.POST.get('account_number', '').strip()
        duitnow_id = request.POST.get('duitnow_id', '').strip()

        if amount < min_withdrawal:
            messages.error(request, f"Jumlah minima pengeluaran adalah RM {min_withdrawal:.2f}.")
            return redirect('payouts:wallet')

        if amount > user.wallet_balance:
            messages.error(request, "Baki wallet anda tidak mencukupi untuk membuat pengeluaran ini.")
            return redirect('payouts:wallet')

        if not recipient_name:
            messages.error(request, "Sila masukkan nama penuh penerima.")
            return redirect('payouts:wallet')

        # Tolak baki wallet clipper
        user.wallet_balance -= amount
        user.save(update_fields=['wallet_balance'])

        # Cipta rekod pengeluaran
        ref = f"WD-{uuid.uuid4().hex[:8].upper()}"
        PayoutRequest.objects.create(
            clipper=user,
            reference=ref,
            amount=amount,
            method=method,
            recipient_name=recipient_name,
            bank_name=bank_name,
            account_number=account_number,
            duitnow_id=duitnow_id,
            status='pending'
        )

        messages.success(request, f"Permohonan pengeluaran RM {amount:.2f} (Rujukan: {ref}) telah dihantar! Dana akan dipindahkan dalam 24 jam.")
        return redirect('payouts:wallet')

    context = {
        'user': user,
        'payout_history': payout_history,
        'min_withdrawal': min_withdrawal,
    }
    return render(request, 'payouts/wallet.html', context)

@login_required
def admin_payouts_view(request):
    """Pengurusan pengeluaran untuk admin"""
    if not (request.user.is_staff or request.user.role == 'admin'):
        messages.error(request, "Hanya admin dibenarkan mengakses laman ini.")
        return redirect('campaigns:index')

    payouts = PayoutRequest.objects.all().order_by('-created_at')
    return render(request, 'payouts/admin_list.html', {'payouts': payouts})

@login_required
def admin_approve_view(request, pk):
    if not (request.user.is_staff or request.user.role == 'admin'):
        return redirect('campaigns:index')

    payout = get_object_or_404(PayoutRequest, pk=pk)
    payout.status = 'completed'
    payout.paid_at = timezone.now()
    payout.save(update_fields=['status', 'paid_at'])

    messages.success(request, f"Pengeluaran {payout.reference} berjaya ditandakan selesai dibayar.")
    return redirect('payouts:admin_list')
