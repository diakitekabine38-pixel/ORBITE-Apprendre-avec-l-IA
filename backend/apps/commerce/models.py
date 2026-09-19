from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel


class Coupon(TimeStampedModel):
    DISCOUNT_PERCENT = "percent"
    DISCOUNT_AMOUNT = "amount"

    DISCOUNT_CHOICES = [
        (DISCOUNT_PERCENT, "Pourcentage"),
        (DISCOUNT_AMOUNT, "Montant"),
    ]

    code = models.CharField(max_length=32, unique=True)
    discount_type = models.CharField(max_length=16, choices=DISCOUNT_CHOICES, default=DISCOUNT_PERCENT)
    value = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(default=0)
    used_count = models.PositiveIntegerField(default=0)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    courses = models.ManyToManyField("courses.Course", related_name="coupons", blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False
        return True

    def apply(self, amount):
        if not self.is_valid:
            raise ValueError("Coupon invalide.")
        if amount < self.min_amount:
            raise ValueError("Montant minimal non atteint.")
        if self.discount_type == self.DISCOUNT_PERCENT:
            discount = (amount * self.value) / Decimal("100")
        else:
            discount = self.value
        return max(Decimal("0"), amount - discount)


class Cart(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="cart", on_delete=models.CASCADE)

    def __str__(self):
        return f"Panier de {self.user}"

    @property
    def total(self):
        return sum(
            (item.course.price or Decimal("0")) for item in self.items.select_related("course__category")
        )


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    course = models.ForeignKey("courses.Course", related_name="cart_items", on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["cart", "course"]

    def __str__(self):
        return f"{self.cart.user} + {self.course}"


class Order(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"
    STATUS_REFUNDED = "refunded"

    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_PROCESSING, "En cours"),
        (STATUS_PAID, "Payée"),
        (STATUS_FAILED, "Échouée"),
        (STATUS_CANCELLED, "Annulée"),
        (STATUS_REFUNDED, "Remboursée"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.CASCADE)
    reference = models.CharField(max_length=64, unique=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.CharField(max_length=8, default="XOF")
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} — {self.user} ({self.status})"


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    course = models.ForeignKey("courses.Course", on_delete=models.SET_NULL, null=True)
    course_title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.course_title