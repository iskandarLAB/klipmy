import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from campaigns.models import Campaign
from submissions.models import ClipSubmission, ViewLog
from payouts.models import PayoutRequest
from payments.models import DepositPayment

def run_seed():
    print("Mula memuatkan data demo KlipMY...")

    # 1. Admin
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@klipmy.com',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    admin_user.set_password('admin123')
    admin_user.save()

    # 2. Demo Brand
    brand_user, _ = User.objects.get_or_create(
        username='brand_senja',
        defaults={
            'email': 'marketing@kopisenja.my',
            'role': 'brand',
            'phone': '01123456789',
        }
    )
    brand_user.set_password('brand123')
    brand_user.save()

    # 3. Demo Clipper
    clipper_user, _ = User.objects.get_or_create(
        username='akramclipper',
        defaults={
            'email': 'akram@gmail.com',
            'role': 'clipper',
            'phone': '0198765432',
            'tiktok_handle': '@akram_clips',
            'instagram_handle': '@akram_reels',
            'bank_name': 'maybank',
            'bank_account_no': '164012998877',
            'duitnow_id': '0198765432',
            'wallet_balance': Decimal('148.50'),
            'total_earned': Decimal('268.50'),
        }
    )
    clipper_user.set_password('clipper123')
    clipper_user.save()

    # 4. Campaigns
    c1, _ = Campaign.objects.get_or_create(
        title="Podcast Sembang Santai Ep. 34: Formula Capai RM10k Pertama",
        defaults={
            'brand': brand_user,
            'brand_name': 'Sembang Santai Podcast',
            'category': 'podcast',
            'description': 'Cari klip-klip kelakar, emosional atau tips bisnes padu daripada episod ini untuk dijadikan short video 15-45 saat.',
            'raw_video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'target_platforms': 'both',
            'required_hashtags': '#SembangSantai #BisnesViral #TipsKewangan #KlipMY',
            'guidelines': '1. Wajib letak hook pada 3 saat terawal.\n2. Wajib letak hashtag yang ditetapkan.\n3. Klip mesti mempunyai sari kata (subtitles) jelas.',
            'budget_total': Decimal('1000.00'),
            'budget_spent': Decimal('285.00'),
            'rate_per_1k_views': Decimal('12.00'),
            'max_payout_per_clip': Decimal('120.00'),
            'status': 'active',
            'is_featured': True,
        }
    )

    c2, _ = Campaign.objects.get_or_create(
        title="Promo Sambal Garing Meletop: Babak Reaksi Pedas Meleleh",
        defaults={
            'brand': brand_user,
            'brand_name': 'Dapur Che Nom Meriah',
            'category': 'fnb',
            'description': 'Klip video reaksi orang makan sambal kami. Cari babak muka berpeluh, bunyi crunch dan ekspresi sedap melampau.',
            'raw_video_url': 'https://drive.google.com/drive/folders/sample-demo-assets',
            'target_platforms': 'tiktok',
            'required_hashtags': '#SambalGaringMeletop #PedasGila #MakanTikTok #KlipMY',
            'guidelines': '1. Fokus kepada bunyi ASMR makan dan reaksi jujur.\n2. Gunakan lagu trending TikTok terkini.\n3. Jangan potong logo produk.',
            'budget_total': Decimal('600.00'),
            'budget_spent': Decimal('160.00'),
            'rate_per_1k_views': Decimal('10.00'),
            'max_payout_per_clip': Decimal('80.00'),
            'status': 'active',
            'is_featured': False,
        }
    )

    c3, _ = Campaign.objects.get_or_create(
        title="Webinar AI & Automation: Cara Automasi Bisnes Shopee 2026",
        defaults={
            'brand': brand_user,
            'brand_name': 'TechNusantara Academy',
            'category': 'education',
            'description': 'Bantu kami sebarkan intipati penting daripada kelas AI automation kami. Klip potongan 30 saat tentang ChatGPT dan Bot jualan.',
            'raw_video_url': 'https://drive.google.com/drive/folders/sample-demo-ai',
            'target_platforms': 'reels',
            'required_hashtags': '#AIBisnes #ShopeeSellerMY #TechMalaysia #KlipMY',
            'guidelines': '1. Minimum 20 saat durasi video.\n2. Letak teks tajuk besar di bahagian atas video.',
            'budget_total': Decimal('800.00'),
            'budget_spent': Decimal('50.00'),
            'rate_per_1k_views': Decimal('15.00'),
            'max_payout_per_clip': Decimal('150.00'),
            'status': 'active',
            'is_featured': False,
        }
    )

    # 5. Sample Submissions for Clipper
    sub1, _ = ClipSubmission.objects.get_or_create(
        campaign=c1,
        video_id="tt_71239847291823749",
        defaults={
            'clipper': clipper_user,
            'platform': 'tiktok',
            'video_url': 'https://www.tiktok.com/@akram_clips/video/71239847291823749',
            'creator_handle': '@akram_clips',
            'status': 'approved',
            'initial_views': 500,
            'current_views': 18500,
            'verified_views': 18000,
            'earnings': Decimal('120.00'),  # Capped at max payout
            'paid_to_wallet': True,
        }
    )

    sub2, _ = ClipSubmission.objects.get_or_create(
        campaign=c2,
        video_id="ig_CxYz9912091",
        defaults={
            'clipper': clipper_user,
            'platform': 'reels',
            'video_url': 'https://www.instagram.com/reel/CxYz9912091/',
            'creator_handle': '@akram_reels',
            'status': 'approved',
            'initial_views': 200,
            'current_views': 5050,
            'verified_views': 4850,
            'earnings': Decimal('48.50'),
            'paid_to_wallet': True,
        }
    )

    # 6. Sample Payout Record
    PayoutRequest.objects.get_or_create(
        reference="WD-20261005-001",
        defaults={
            'clipper': clipper_user,
            'amount': Decimal('120.00'),
            'method': 'duitnow',
            'recipient_name': 'Akram Bin Razali',
            'duitnow_id': '0198765432',
            'status': 'completed',
        }
    )

    print("Data demo berjaya dimuatkan dengan sempurna!")
    print("Akaun Demo:")
    print(" - Clipper : username 'akramclipper', password 'clipper123'")
    print(" - Brand   : username 'brand_senja', password 'brand123'")
    print(" - Admin   : username 'admin', password 'admin123'")

if __name__ == '__main__':
    run_seed()
