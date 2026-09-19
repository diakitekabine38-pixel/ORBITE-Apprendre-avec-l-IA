from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("methods", views.PaymentMethodViewSet, basename="payment-method")
router.register("payments", views.PaymentViewSet, basename="payment")
router.register("transactions", views.TransactionViewSet, basename="payment-transaction")

urlpatterns = router.urls