"""PaymentService abstraction.

New providers (Orange Money, card, mobile) plug in behind this interface
without touching the commerce logic.
"""
import json

from django.conf import settings
from django.utils import timezone

from .models import Payment, PaymentTransaction


class BasePaymentProvider:
    code = "base"

    def initialize(self, payment):
        raise NotImplementedError

    def verify(self, payment):
        raise NotImplementedError


class ManualProvider(BasePaymentProvider):
    """Dev/phase-1 provider: payment confirmed by the admin panel."""

    code = "manual"

    def initialize(self, payment):
        PaymentTransaction.objects.create(
            payment=payment, status="initiated", payload={"provider": self.code}
        )
        return {"checkout_url": None, "status": "pending", "action": "manual"}

    def verify(self, payment, provider_reference="", **payload):
        payment.status = Payment.STATUS_PAID
        payment.verified_at = timezone.now()
        payment.payload = payload
        payment.save(update_fields=["status", "verified_at", "payload", "updated_at"])
        PaymentTransaction.objects.create(
            payment=payment,
            provider_reference=provider_reference or "MANUAL-OK",
            status="confirmed",
            payload=payload,
        )
        return payment


class StripeProvider(BasePaymentProvider):
    """Real PSP (Stripe Checkout). Active seulement si ORBITE_STRIPE_SECRET_KEY est défini.

    Le frontend reçoit un `checkout_url` (Stripe Checkout Session) ; le webhook
    `checkout.session.completed` appelle `PaymentService.confirm` à la validation.
    """

    code = "stripe"

    def __init__(self):
        self.secret_key = getattr(settings, "ORBITE_STRIPE_SECRET_KEY", "")
        self.publishable_key = getattr(settings, "ORBITE_STRIPE_PUBLISHABLE_KEY", "")
        self.webhook_secret = getattr(settings, "ORBITE_STRIPE_WEBHOOK_SECRET", "")

    def is_configured(self):
        return bool(self.secret_key)

    def initialize(self, payment):
        if not self.is_configured():
            raise RuntimeError(
                "Le provider Stripe n'est pas configuré : renseignez ORBITE_STRIPE_SECRET_KEY."
            )
        import urllib.parse
        import urllib.request

        site_url = getattr(settings, "ORBITE_SITE_URL", "").rstrip("/")
        payload = {
            "mode": "payment",
            "success_url": f"{site_url}/student/panier?paiement=reussi",
            "cancel_url": f"{site_url}/student/panier?paiement=annule",
            "line_items": [
                {
                    "price_data": {
                        "currency": "xof",
                        "unit_amount": int(payment.amount * 100),
                        "product_data": {"name": f"Commande {payment.order.reference}"},
                    },
                    "quantity": 1,
                }
            ],
            # Redirige le webhook vers notre endpoint de confirmation.
            "metadata": {"order_reference": payment.order.reference},
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            "https://api.stripe.com/v1/checkout/sessions", data=data, method="POST"
        )
        request.add_header("Content-Type", "application/json")
        request.add_header("Authorization", f"Bearer {self.secret_key}")
        with urllib.request.urlopen(request, timeout=20) as response:
            session = json.loads(response.read().decode("utf-8"))

        PaymentTransaction.objects.create(
            payment=payment,
            provider_reference=session.get("id", ""),
            status="checkout_started",
            payload={"checkout_url": session.get("url", "")},
        )
        return {
            "checkout_url": session.get("url"),
            "checkout_session_id": session.get("id"),
            "status": "pending",
            "action": "stripe",
        }

    def verify(self, payment, provider_reference="", **payload):
        payment.status = Payment.STATUS_PAID
        payment.verified_at = timezone.now()
        payment.payload = payload
        payment.save(update_fields=["status", "verified_at", "payload", "updated_at"])
        PaymentTransaction.objects.create(
            payment=payment,
            provider_reference=provider_reference or "STRIPE-OK",
            status="confirmed",
            payload=payload,
        )
        return payment


class PaymentService:
    def __init__(self, provider_code=None):
        provider_code = provider_code or getattr(settings, "ORBITE_PAYMENT_PROVIDER", "manual")
        self.provider = self._resolve(provider_code)

    def _resolve(self, code):
        providers = {"manual": ManualProvider, "stripe": StripeProvider}
        provider_cls = providers.get(code, ManualProvider)
        return provider_cls()

    def initialize(self, order, method):
        payment, _ = Payment.objects.get_or_create(
            order=order, defaults={"method": method, "amount": order.total}
        )
        return self.provider.initialize(payment)

    @staticmethod
    def confirm(payment, **kwargs):
        """Server-side verification → triggers order confirmation."""
        if payment.status in (Payment.STATUS_PAID, Payment.STATUS_REFUNDED):
            return payment
        provider = PaymentService(payment.method.code).provider
        payment = provider.verify(payment, **kwargs)
        from apps.commerce.services import confirm_paid_order

        confirm_paid_order(payment.order)
        return payment