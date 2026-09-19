from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsAdminOrOwner
from apps.commerce.models import Order

from .models import Payment, PaymentMethod
from .serializers import (
    PaymentMethodSerializer,
    PaymentSerializer,
    PaymentTransactionSerializer,
)


class PaymentMethodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [AllowAny]


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        qs = Payment.objects.select_related("order", "order__user", "method")
        return qs if self.request.user.is_admin() else qs.filter(order__user=self.request.user)

    @action(detail=False, methods=["post"])
    def start(self, request):
        """Create and initialise a payment for an order (server-side trust)."""
        from apps.payments.service import PaymentService

        try:
            order = Order.objects.get(
                reference=request.data.get("order_reference"), user=request.user
            )
        except Order.DoesNotExist:
            return Response({"detail": "Commande introuvable."}, status=404)
        if order.status != Order.STATUS_PENDING:
            return Response({"detail": "Commande non payable."}, status=400)

        method_code = request.data.get("provider", "manual")
        method = PaymentMethod.objects.filter(code=method_code, is_active=True).first()
        if not method:
            return Response({"detail": "Moyen de paiement indisponible."}, status=400)

        service = PaymentService(method.code)
        result = service.initialize(order, method)
        payment = Payment.objects.get(order=order)
        return Response(
            {"payment": PaymentSerializer(payment).data, "step": result},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def confirm(self, request):
        """Webhook-like endpoint: mark a payment confirmed after verification."""
        from apps.payments.service import PaymentService

        try:
            payment = Payment.objects.get(
                order__reference=request.data.get("order_reference"), order__user=request.user
            )
        except Payment.DoesNotExist:
            return Response({"detail": "Paiement introuvable."}, status=404)

        PaymentService.confirm(payment, provider_reference=request.data.get("reference", ""))
        order = payment.order
        order.refresh_from_db()
        return Response({"order_reference": order.reference, "order_status": order.status})


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        qs = PaymentTransaction.objects.select_related("payment__order__user")
        if self.request.user.is_admin():
            return qs
        return qs.filter(payment__order__user=self.request.user)