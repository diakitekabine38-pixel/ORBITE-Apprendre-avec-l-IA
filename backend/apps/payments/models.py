from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class PaymentMethod(TimeStampedModel):
    name = models.CharField(max_length=80)
    code = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Payment(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"
    STATUS_REFUNDED = "refunded"

    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_PROCESSING, "En cours"),
        (STATUS_PAID, "Payé"),
        (STATUS_FAILED, "Échoué"),
        (STATUS_CANCELLED, "Annulé"),
        (STATUS_REFUNDED, "Remboursé"),
    ]

    order = models.OneToOneField(
        "commerce.Order", related_name="payment", on_delete=models.CASCADE
    )
    method = models.ForeignKey(
        PaymentMethod, related_name="payments", on_delete=models.PROTECT
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.order} — {self.status}"


class PaymentTransaction(TimeStampedModel):
    payment = models.ForeignKey(Payment, related_name="transactions", on_delete=models.CASCADE)
    provider_reference = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=32, default="initiated")
    payload = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.payment} — {self.status}"