import base64
import json
import logging
import requests
from decimal import Decimal
from django.conf import settings
from django.core.cache import cache
from django.urls import reverse
from cryptography.exceptions import InvalidSignature as CryptoInvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from . import GatewayError, InvalidSignature

logger = logging.getLogger(__name__)

PUBLIC_KEY_CACHE = "chip_public_key_cache"

def _to_cents(amount: Decimal) -> int:
    return int(round(amount * 100))

class ChipGateway:
    name = "chip"

    def __init__(self):
        self.secret_key = getattr(settings, 'CHIP_SECRET_KEY', '')
        self.brand_id = getattr(settings, 'CHIP_BRAND_ID', '')
        self.base = getattr(settings, 'CHIP_API_BASE', 'https://gate.chip-in.asia/api/v1/').rstrip('/')
        self.headers = {"Authorization": f"Bearer {self.secret_key}"}

    def is_configured(self) -> bool:
        return bool(self.secret_key and self.brand_id)

    def _request(self, method, path, **kwargs):
        if not self.is_configured():
            raise GatewayError("CHIP_SECRET_KEY dan CHIP_BRAND_ID belum ditetapkan.")
        try:
            r = requests.request(method, f"{self.base}{path}", headers=self.headers, timeout=20, **kwargs)
        except requests.RequestException as e:
            raise GatewayError(f"Ralat sambungan ke gateway CHIP: {e}") from e
        
        if r.status_code >= 400:
            logger.error("CHIP Error %s %s -> %s %s", method, path, r.status_code, r.text[:500])
            raise GatewayError(f"CHIP ralat {r.status_code}: {r.text[:300]}")
        return r.json()

    def create_purchase(self, payment_record, request=None):
        """
        Mencipta purchase dalam CHIP Collect.
        """
        campaign = payment_record.campaign
        user = payment_record.user
        amount = payment_record.amount
        
        site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
        return_url = f"{site_url}{reverse('payments:return_page')}?ref={payment_record.reference}"
        
        # Jika belum configure credential sebenar, kembalikan URL sandbox simulasi tempatan
        if not self.is_configured():
            mock_checkout_url = f"{site_url}{reverse('payments:mock_checkout', kwargs={'reference': payment_record.reference})}"
            payment_record.chip_purchase_id = f"mock_{payment_record.reference}"
            payment_record.checkout_url = mock_checkout_url
            payment_record.save()
            return {
                "purchase_id": payment_record.chip_purchase_id,
                "checkout_url": mock_checkout_url,
                "is_mock": True
            }

        client_info = {
            "email": user.email or f"{user.username}@example.com",
            "full_name": (user.get_full_name() or user.username)[:128]
        }
        if user.phone:
            client_info["phone"] = user.phone

        body = {
            "brand_id": self.brand_id,
            "reference": payment_record.reference,
            "client": client_info,
            "purchase": {
                "currency": "MYR",
                "products": [
                    {
                        "name": f"Deposit Bajet: {campaign.title}"[:256],
                        "price": _to_cents(amount),
                        "quantity": "1"
                    }
                ],
                "notes": f"Kempen #{campaign.id}: {campaign.title}"
            },
            "payment_method_whitelist": ["fpx", "card"],
            "success_redirect": return_url,
            "failure_redirect": return_url,
            "cancel_redirect": return_url,
            "send_receipt": True,
        }

        callback_url = f"{site_url}{reverse('payments:callback')}"
        if callback_url.startswith("https://"):
            body["success_callback"] = callback_url

        data = self._request("POST", "/purchases/", json=body)
        payment_record.chip_purchase_id = data.get("id")
        payment_record.checkout_url = data.get("checkout_url")
        payment_record.save()

        return {
            "purchase_id": data.get("id"),
            "checkout_url": data.get("checkout_url"),
            "is_mock": False
        }

    def verify_callback(self, raw_body: bytes, signature_b64: str) -> dict:
        """Sahkan tandatangan webhook X-Signature menggunakan public key CHIP."""
        if not signature_b64:
            raise InvalidSignature("Tiada header X-Signature.")

        # Ambil public key
        pub_pem = getattr(settings, 'CHIP_PUBLIC_KEY', None)
        if not pub_pem:
            pub_pem = cache.get(PUBLIC_KEY_CACHE)
            if not pub_pem:
                pub_pem = self._request("GET", "/public_key/")
                cache.set(PUBLIC_KEY_CACHE, pub_pem, 86400)

        try:
            pub = load_pem_public_key(pub_pem.encode('utf-8'))
            pub.verify(
                base64.b64decode(signature_b64),
                raw_body,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
        except (CryptoInvalidSignature, ValueError, TypeError) as e:
            raise InvalidSignature(f"Tandatangan digital CHIP tidak sah: {e}") from e

        data = json.loads(raw_body)
        if data.get("brand_id") and data["brand_id"] != self.brand_id:
            raise InvalidSignature("Brand ID tidak sepadan.")
        return data
