from rest_framework import serializers

from .models import Payment, PaymentMethod, PaymentTransaction


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ["id", "name", "code", "is_active"]


class PaymentSerializer(serializers.ModelSerializer):
    order_reference = serializers.CharField(source="order.reference", read_only=True)
    method_name = serializers.CharField(source="method.name", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "order_reference",
            "method",
            "method_name",
            "amount",
            "status",
            "verified_at",
        ]
        read_only_fields = fields


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ["id", "payment", "provider_reference", "status", "payload", "created_at"]
        read_only_fields = fields