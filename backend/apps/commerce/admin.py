from django.contrib import admin

from .models import Cart, CartItem, Coupon, Order, OrderItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "course")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "user", "status", "total", "created_at")
    list_filter = ("status",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "course_title", "price")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "value", "is_active")