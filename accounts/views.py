from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User

def register_view(request):
    if request.user.is_authenticated:
        return redirect('campaigns:index')

    role_param = request.GET.get('role', 'clipper')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        role = request.POST.get('role', 'clipper')
        phone = request.POST.get('phone', '').strip()
        tiktok_handle = request.POST.get('tiktok_handle', '').strip()
        instagram_handle = request.POST.get('instagram_handle', '').strip()

        if not username or not password:
            messages.error(request, "Sila lengkapkan nama pengguna dan kata laluan.")
            return render(request, 'accounts/register.html', {'role': role})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Nama pengguna ini telah digunakan. Sila pilih yang lain.")
            return render(request, 'accounts/register.html', {'role': role})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            phone=phone,
            tiktok_handle=tiktok_handle,
            instagram_handle=instagram_handle
        )
        login(request, user)
        messages.success(request, f"Selamat datang ke KlipMY, {user.username}! Akaun anda sebagai {user.get_role_display()} sedia digunakan.")
        if user.is_brand:
            return redirect('campaigns:create')
        return redirect('campaigns:index')

    return render(request, 'accounts/register.html', {'role': role_param})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('campaigns:index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Selamat kembali, {user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('campaigns:index')
        else:
            messages.error(request, "Nama pengguna atau kata laluan tidak sah.")

    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Anda telah log keluar dengan selamat.")
    return redirect('campaigns:index')

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        user.phone = request.POST.get('phone', '').strip()
        user.tiktok_handle = request.POST.get('tiktok_handle', '').strip()
        user.instagram_handle = request.POST.get('instagram_handle', '').strip()
        user.bank_name = request.POST.get('bank_name', '')
        user.bank_account_no = request.POST.get('bank_account_no', '').strip()
        user.duitnow_id = request.POST.get('duitnow_id', '').strip()
        user.save()
        messages.success(request, "Profil dan maklumat DuitNow anda berjaya dikemaskini!")
        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {'user': user, 'banks': User.BANK_CHOICES})

@login_required
def switch_role_demo(request):
    """Fungsi pembantu: Tukar peranan antara Clipper dan Brand dengan 1-klik untuk tujuan demo/testing"""
    user = request.user
    user.role = 'brand' if user.role == 'clipper' else 'clipper'
    user.save(update_fields=['role'])
    messages.info(request, f"Mod bertukar kepada: {user.get_role_display()}")
    if user.is_brand:
        return redirect('campaigns:brand_dashboard')
    return redirect('campaigns:index')
