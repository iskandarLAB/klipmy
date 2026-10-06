from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from accounts.models import User
from campaigns.models import Campaign
from submissions.models import ClipSubmission
from submissions.services import parse_video_url, update_submission_views
from payments.models import DepositPayment
from payouts.models import PayoutRequest

class KlipMYSystemIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.brand = User.objects.create_user(username='test_brand', password='password123', role='brand')
        self.clipper = User.objects.create_user(username='test_clipper', password='password123', role='clipper', wallet_balance=Decimal('100.00'))
        self.campaign = Campaign.objects.create(
            brand=self.brand,
            title='Kempen Podcast Viral 2026',
            brand_name='Jenama Ujian',
            raw_video_url='https://youtu.be/test',
            target_platforms='both',
            required_hashtags='#UjianKlip #KlipMY',
            budget_total=Decimal('500.00'),
            rate_per_1k_views=Decimal('10.00'),
            max_payout_per_clip=Decimal('100.00'),
            status='active'
        )

    def test_parse_tiktok_and_reels_url(self):
        tt_url = 'https://www.tiktok.com/@myuser/video/7123456789012345678'
        res_tt = parse_video_url(tt_url)
        self.assertEqual(res_tt['platform'], 'tiktok')
        self.assertEqual(res_tt['video_id'], 'tt_7123456789012345678')

        ig_url = 'https://www.instagram.com/reel/C3_aBcDeF12/'
        res_ig = parse_video_url(ig_url)
        self.assertEqual(res_ig['platform'], 'reels')
        self.assertEqual(res_ig['video_id'], 'ig_C3_aBcDeF12')

    def test_clipper_submit_video_flow(self):
        self.client.login(username='test_clipper', password='password123')
        response = self.client.post(reverse('submissions:submit', kwargs={'campaign_id': self.campaign.id}), {
            'video_url': 'https://www.tiktok.com/@testuser/video/99887766554433'
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        submission = ClipSubmission.objects.filter(campaign=self.campaign, clipper=self.clipper).first()
        self.assertIsNotNone(submission)
        self.assertEqual(submission.platform, 'tiktok')
        self.assertGreater(submission.verified_views, 0)
        self.assertGreater(submission.earnings, Decimal('0.00'))

    def test_chip_payment_checkout_and_activation(self):
        self.client.login(username='test_brand', password='password123')
        new_campaign = Campaign.objects.create(
            brand=self.brand,
            title='Kempen Baru Belum Bayar',
            brand_name='Jenama Ujian 2',
            raw_video_url='https://youtu.be/test2',
            budget_total=Decimal('300.00'),
            status='pending_payment'
        )
        
        # Trigger checkout
        response = self.client.get(reverse('payments:checkout', kwargs={'campaign_id': new_campaign.id}), follow=True)
        self.assertEqual(response.status_code, 200)

        # Mock complete payment
        payment = DepositPayment.objects.filter(campaign=new_campaign).first()
        self.assertIsNotNone(payment)
        
        post_res = self.client.post(reverse('payments:mock_checkout', kwargs={'reference': payment.reference}), {
            'bank': 'Maybank2u'
        }, follow=True)
        self.assertEqual(post_res.status_code, 200)

        new_campaign.refresh_from_db()
        self.assertEqual(new_campaign.status, 'active')

    def test_payout_withdrawal_request(self):
        self.client.login(username='test_clipper', password='password123')
        response = self.client.post(reverse('payouts:wallet'), {
            'amount': '50.00',
            'method': 'duitnow',
            'recipient_name': 'Test Clipper Name',
            'duitnow_id': '0123456789'
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        self.clipper.refresh_from_db()
        self.assertEqual(self.clipper.wallet_balance, Decimal('50.00'))
        
        payout = PayoutRequest.objects.filter(clipper=self.clipper).first()
        self.assertIsNotNone(payout)
        self.assertEqual(payout.amount, Decimal('50.00'))
        self.assertEqual(payout.status, 'pending')
