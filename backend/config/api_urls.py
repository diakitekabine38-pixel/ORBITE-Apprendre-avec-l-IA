from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.users.urls")),
    path("users/", include("apps.users.api_urls")),
    path("courses/", include("apps.courses.urls")),
    path("learning/", include("apps.learning.urls")),
    path("assessments/", include("apps.assessments.urls")),
    path("ai/", include("apps.ai.urls")),
    path("cart/", include("apps.commerce.cart_urls")),
    path("orders/", include("apps.commerce.order_urls")),
    path("payments/", include("apps.payments.urls")),
    path("certificates/", include("apps.certificates.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("analytics/", include("apps.analytics.urls")),
]