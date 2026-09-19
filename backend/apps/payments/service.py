"""PaymentService abstraction.

New providers (Orange Money, card, mobile) plug in behind this interface
without touching the commerce logic.
"""
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


class PaymentService:
    def __init__(self, provider_code=None):
        provider_code = provider_code or getattr(settings, "ORBITE_PAYMENT_PROVIDER", "manual")
        self.provider = self._resolve(provider_code)

    def _resolve(self, code):
        providers = {"manual": ManualProvider}
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