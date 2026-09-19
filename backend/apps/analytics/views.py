from django.db.models import Count, Sum
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsAdminUser

from .models import Event
from .serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        qs = Event.objects.select_related("user")
        return qs.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = dict(request.data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DashboardStatsViewSet(viewsets.ViewSet):
    """Admin analytics — platform / course / AI dimensions."""

    permission_classes = [IsAdminUser]

    @action(detail=False, methods=["get"])
    def overview(self, request):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        from apps.courses.models import Course, Review
        from apps.learning.models import Enrollment
        from apps.commerce.models import Order

        now = timezone.now()
        return Response(
            {
                "users": User.objects.count(),
                "students": User.objects.filter(role=User.ROLE_STUDENT).count(),
                "published_courses": Course.objects.filter(status=Course.STATUS_PUBLISHED).count(),
                "enrollments": Enrollment.objects.count(),
                "orders_total": Order.objects.filter(status=Order.STATUS_PAID).count(),
                "revenue": Order.objects.filter(status=Order.STATUS_PAID).aggregate(
                    s=Sum("total")
                )["s"],
                "reviews": Review.objects.filter(status=Review.STATUS_APPROVED).count(),
                "events_24h": Event.objects.filter(created_at__gte=now - timezone.timedelta(hours=24)).count(),
            }
        )