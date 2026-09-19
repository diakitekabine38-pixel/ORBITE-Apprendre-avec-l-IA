from decimal import Decimal

from rest_framework import serializers

from .models import Cart, CartItem, Coupon, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    price = serializers.DecimalField(source="course.price", max_digits=10, decimal_places=2, read_only=True)
    course_slug = serializers.CharField(source="course.slug", read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "course", "course_title", "course_slug", "price", "added_at"]
        read_only_fields = ["id", "added_at"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "total"]


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ["code", "discount_type", "value", "valid_from", "valid_to", "max_uses"]
        read_only_fields = fields


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "course", "course_title", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "reference",
            "status",
            "subtotal",
            "discount",
            "total",
            "currency",
            "items",
            "created_at",
            "paid_at",
        ]
        read_only_fields = fields


class CheckoutSerializer(serializers.Serializer):
    course_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.CharField(required=False, default="manual")