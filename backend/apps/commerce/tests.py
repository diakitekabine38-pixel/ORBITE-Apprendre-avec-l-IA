from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.commerce.models import Cart, Coupon, Order, OrderItem
from apps.commerce.services import create_order
from apps.common.tests import make_course, make_user


class CheckoutTests(TestCase):
    def setUp(self):
        self.student = make_user("client")
        self.instructor = make_user("prof", role="instructor")
        Coupon.objects.get_or_create(
            code="ORBIT10",
            defaults={
                "discount_type": Coupon.DISCOUNT_PERCENT,
                "value": 10,
                "valid_from": timezone.now() - timezone.timedelta(days=1),
                "valid_to": timezone.now() + timezone.timedelta(days=30),
            },
        )

    def test_order_total_with_coupon(self):
        c1 = make_course(instructor=self.instructor, price=20000, title="Alpha")
        c2 = make_course(instructor=self.instructor, price=0, title="Gratuite")
        order = create_order(self.student, [c1.id, c2.id], coupon_code="ORBIT10")
        # 10% off the paid course only
        self.assertEqual(order.subtotal, 20000)
        self.assertEqual(order.discount, 2000)
        self.assertEqual(order.total, 18000)
        self.assertEqual(order.status, Order.STATUS_PENDING)
        self.assertEqual(order.items.count(), 2)

    def test_coupon_expired_rejected(self):
        course = make_course(instructor=self.instructor, price=5000, title="Beta")
        Coupon.objects.create(
            code="EXPIRE",
            discount_type=Coupon.DISCOUNT_PERCENT,
            value=50,
            valid_to=timezone.now() - timezone.timedelta(days=1),
        )
        with self.assertRaises(ValueError):
            create_order(self.student, [course.id], coupon_code="EXPIRE")

    def test_empty_cart_rejected(self):
        with self.assertRaises(ValueError):
            create_order(self.student, [])


class CartApiTests(APITestCase):
    def setUp(self):
        self.student = make_user("cartiste")
        self.instructor = make_user("prof", role="instructor")
        self.course = make_course(instructor=self.instructor, price=5000, title="À acheter")

    def test_add_remove_summary(self):
        self.client.force_authenticate(self.student)
        add = self.client.post("/api/v1/cart/add/", {"course_id": self.course.id}, format="json")
        self.assertEqual(add.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(add.data["items"]), 1)

        summary = self.client.get("/api/v1/cart/summary/")
        self.assertEqual(float(summary.data["total"]), 5000)

        remove = self.client.post(
            "/api/v1/cart/remove/", {"course_id": self.course.id}, format="json"
        )
        self.assertEqual(len(remove.data["items"]), 0)

    def test_free_course_not_added_to_cart(self):
        free = make_course(instructor=self.instructor, price=0, title="Gratuite cart")
        self.client.force_authenticate(self.student)
        response = self.client.post("/api/v1/cart/add/", {"course_id": free.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OrderApiTests(APITestCase):
    def setUp(self):
        self.student = make_user("client2")
        self.instructor = make_user("prof", role="instructor")
        self.course = make_course(instructor=self.instructor, price=9000, title="Payante X")

    def test_checkout_and_order_visibility(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            "/api/v1/orders/checkout/",
            {"course_ids": [self.course.id]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        reference = response.data["reference"]

        orders = self.client.get("/api/v1/orders/")
        self.assertEqual(orders.data["count"], 1)

        other = make_user("autre2")
        self.client.force_authenticate(other)
        orders = self.client.get("/api/v1/orders/")
        self.assertEqual(orders.data["count"], 0)
        detail = self.client.get(f"/api/v1/orders/{Order.objects.get(reference=reference).id}/")
        self.assertEqual(detail.status_code, status.HTTP_404_NOT_FOUND)