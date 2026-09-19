"""Commerce service: checkout, payment confirmation, enrollment activation.

The backend is the single source of truth for order status: the frontend never
decides whether an order is paid.
"""
import uuid
from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import Cart, Coupon, Order, OrderItem


def create_reference():
    return f"ORB-{uuid.uuid4().hex[:10].upper()}"


@transaction.atomic
def create_order(user, course_ids, coupon_code=None):
    """Build an order from the given courses (fallback: current cart)."""
    from apps.courses.models import Course

    if course_ids:
        courses = list(Course.objects.filter(pk__in=course_ids, status=Course.STATUS_PUBLISHED))
    else:
        cart, _ = Cart.objects.get_or_create(user=user)
        courses = [item.course for item in cart.items.select_related("course")]

    if not courses:
        raise ValueError("Panier vide.")

    subtotal = sum((c.price or Decimal("0")) for c in courses)
    coupon = None
    discount = Decimal("0")

    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code.upper()).first()
        if not coupon or not coupon.is_valid:
            raise ValueError("Coupon invalide ou expiré.")
        if subtotal >= coupon.min_amount:
            discounted = coupon.apply(subtotal)
            discount = subtotal - discounted
            coupon.used_count = F("used_count") + 1
            coupon.save(update_fields=["used_count"])
        else:
            raise ValueError("Montant minimal du coupon non atteint.")

    order = Order.objects.create(
        user=user,
        reference=create_reference(),
        status=Order.STATUS_PENDING,
        subtotal=subtotal,
        discount=discount,
        total=subtotal - discount,
        coupon=coupon,
    )
    for course in courses:
        OrderItem.objects.create(
            order=order, course=course, course_title=course.title, price=course.price or 0
        )
    return order


@transaction.atomic
def confirm_paid_order(order):
    """Once payment is verified server-side, grant access and notify."""
    from apps.learning.models import Enrollment
    from apps.payments.models import Payment

    if order.status == Order.STATUS_PAID:
        return order

    order.status = Order.STATUS_PAID
    order.paid_at = timezone.now()
    order.save(update_fields=["status", "paid_at", "updated_at"])

    Payment.objects.filter(order=order).update(status=Payment.STATUS_PAID)

    for item in order.items.select_related("course"):
        Enrollment.objects.get_or_create(user=order.user, course=item.course)

    try:
        from apps.notifications.models import Notification

        Notification.objects.create(
            user=order.user,
            notification_type=Notification.TYPE_COMMERCIAL,
            title="Commande confirmée",
            message=f"Votre commande {order.reference} est payée. Accès débloqué !",
        )
    except Exception:
        pass
    return order