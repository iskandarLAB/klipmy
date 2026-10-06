# KlipMY - Platform Video Clipping No. 1 Malaysia 🇲🇾

Platform pasaran *short-form video clipping* alternatif kepada Clippers Farm yang direka khas supaya **jauh lebih ringkas, mesra pengguna (mobile-first), dan terus bersepadu dengan gerbang pembayaran CHIP (FPX) & DuitNow**.

---

## 🌟 Ciri-Ciri Utama & Kelebihan

1. **Mesra Pengguna & Mobile-First**:
   - Reka bentuk antaramuka moden ala aplikasi media sosial (Tailwind CSS).
   - Bar navigasi bawah (bottom navigation) untuk akses pantas di telefon pintar.
2. **Sokongan TikTok & Instagram Reels**:
   - Clipper hanya perlu salin pautan video TikTok atau Reels dan tampal dalam sistem.
   - Pengekstrakan ID video automatik bagi mengelakkan penipuan dan duplikasi video.
3. **Tracking Tontonan (Views) & Pengiraan Duit Real-Time**:
   - Kadar bayaran telus (contoh: RM 10 / 1,000 verified views).
   - Auto-cap bajet mengikut had kempen bagi mengelakkan perbelanjaan berlebihan.
   - Butang *Sync Views* segera untuk clipper melihat baki terkumpul bertambah serta-merta.
4. **Integrasi Gerbang Pembayaran CHIP Asia (FPX)**:
   - Jenama mendepositkan bajet kempen menggunakan CHIP FPX (Maybank2u, CIMB Clicks, Bank Islam, TNG eWallet, dll).
   - Pengesahan keselamatan tandatangan digital RSA PKCS#1 v1.5 untuk webhook callback.
   - Dilengkapi **Sandbox Simulator** sedia ada jika API Key sebenar belum dimasukkan.
5. **Sistem Dompet & Pengeluaran DuitNow**:
   - Clipper boleh memohon pengeluaran wang baki hasil terus ke DuitNow ID (No Telefon / No KP) atau pindahan akaun bank tempatan (Minima RM 20).
   - Panel admin untuk meluluskan permohonan dengan 1 klik.

---

## 🚀 Panduan Memulakan Aplikasi

### 1. Masuk ke direktori projek
```bash
cd /Users/Ridzuan/.gemini/antigravity/scratch/clippers
```

### 2. Jalankan Pelayan Pembangunan
```bash
.venv/bin/python manage.py runserver 127.0.0.1:8000
```
Buka pelayar web anda di: **`http://127.0.0.1:8000`**

---

## 👥 Akaun Demo Sedia Ada

Data demo telah siap diisi dengan kempen aktif dan sampel video:

| Peranan | Username | Kata Laluan | Keterangan |
| :--- | :--- | :--- | :--- |
| **Clipper** | `akramclipper` | `clipper123` | Sudah mempunyai baki wallet RM 148.50 & 2 klip video dihantar. |
| **Brand** | `brand_senja` | `brand123` | Pemilik kempen aktif Kopi Senja & Podcast. |
| **Admin** | `admin` | `admin123` | Akses penuh admin dan pengurusan payout di `/admin/`. |

*(Nota: Terdapat juga butang **"Tukar Mod"** di bahagian atas navigasi untuk menukar pandangan antara Clipper dan Brand dengan 1-klik.)*
