from decimal import Decimal

from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsAdminOrOwner
from apps.courses.models import Course

from . import services
from .models import Cart, CartItem, Coupon, Order
from .serializers import CartSerializer, CheckoutSerializer, CouponSerializer, OrderSerializer


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        qs = Cart.objects.prefetch_related("items__course")
        return qs if self.request.user.is_admin() else qs.filter(user=self.request.user)

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @action(detail=False, methods=["post"])
    def add(self, request):
        cart = self.get_object()
        course = get_object_or_404(Course, pk=request.data.get("course_id"))
        if course.is_free and course.price == 0:
            return Response(
                {"detail": "Cette formation est gratuite : inscrivez-vous directement."}, status=400
            )
        item, created = CartItem.objects.get_or_create(cart=cart, course=course)
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED if created else 200)

    @action(detail=False, methods=["post"])
    def remove(self, request):
        cart = self.get_object()
        CartItem.objects.filter(cart=cart, course_id=request.data.get("course_id")).delete()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        cart = self.get_object()
        return Response(CartSerializer(cart).data)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        qs = Order.objects.prefetch_related("items").select_related("user")
        return qs if self.request.user.is_admin() else qs.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = services.create_order(
                request.user,
                serializer.validated_data.get("course_ids") or [],
                serializer.validated_data.get("coupon_code"),
            )
        except ValueError as error:
            return Response({"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        # Clear the cart items that were ordered.
        if serializer.validated_data.get("course_ids"):
            CartItem.objects.filter(
                cart__user=request.user, course_id__in=serializer.validated_data["course_ids"]
            ).delete()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def coupons(self, request):
        return Response(
            CouponSerializer(
                Coupon.objects.filter(is_active=True), many=True
            ).data
        )