from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsAdminOrOwner

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        qs = Notification.objects.select_related("user")
        return qs if self.request.user.is_admin() else qs.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({"detail": "Notifications marquées comme lues."})

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=["is_read", "updated_at"])
        return Response(NotificationSerializer(notification).data)