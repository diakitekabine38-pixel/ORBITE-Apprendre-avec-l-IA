from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.commerce.services import create_order
from apps.common.tests import make_course, make_user
from apps.learning.models import Enrollment
from apps.payments.models import Payment, PaymentMethod
from apps.payments.service import PaymentService


class PaymentFlowTests(TestCase):
    def setUp(self):
        self.student = make_user("payeur")
        self.instructor = make_user("prof", role="instructor")
        self.method = PaymentMethod.objects.create(name="Vérification manuelle", code="manual")
        self.course = make_course(instructor=self.instructor, price=12000, title="Formation payée")
        self.order = create_order(self.student, [self.course.id])

    def test_payment_confirmation_grants_enrollment(self):
        service = PaymentService("manual")
        result = service.initialize(self.order, self.method)
        self.assertEqual(result["status"], "pending")

        payment = Payment.objects.get(order=self.order)
        PaymentService.confirm(payment, provider_reference="REF-123")

        payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_PAID)
        self.assertEqual(self.order.status, "paid")
        self.assertTrue(Enrollment.objects.filter(user=self.student, course=self.course).exists())

    def test_pending_order_not_paid(self):
        self.order.refresh_from_db()
        self.assertEqual(len(Enrollment.objects.filter(user=self.student, course=self.course)), 0)


class PaymentApiTests(APITestCase):
    def setUp(self):
        self.student = make_user("payapi")
        self.instructor = make_user("prof", role="instructor")
        self.method = PaymentMethod.objects.create(name="Vérification manuelle", code="manual")
        self.course = make_course(instructor=self.instructor, price=6000, title="API Pay")
        self.order = create_order(self.student, [self.course.id])

    def test_start_and_confirm_endpoint(self):
        self.client.force_authenticate(self.student)
        start = self.client.post(
            "/api/v1/payments/payments/start/",
            {"order_reference": self.order.reference, "provider": "manual"},
            format="json",
        )
        self.assertEqual(start.status_code, status.HTTP_201_CREATED)

        confirm = self.client.post(
            "/api/v1/payments/payments/confirm/",
            {"order_reference": self.order.reference, "reference": "API-REF"},
            format="json",
        )
        self.assertEqual(confirm.status_code, status.HTTP_200_OK)
        self.assertEqual(confirm.data["order_status"], "paid")
        self.order.refresh_from_db()
        self.assertTrue(self.order.payment.status == Payment.STATUS_PAID)

    def test_public_methods_list(self):
        response = self.client.get("/api/v1/payments/methods/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = [m["code"] for m in response.data["results"]]
        self.assertIn("manual", codes)