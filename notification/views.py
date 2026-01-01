from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing notifications.
    Automatically filters by the logged-in user.
    """

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )


class NotificationReadView(generics.UpdateAPIView):
    """Mark a single notification as read."""

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch", "put"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_read = True
        instance.save()
        return Response(
            status=status.HTTP_200_OK, data=NotificationSerializer(instance).data
        )


class NotificationUnreadView(generics.UpdateAPIView):
    """Mark a single notification as unread."""

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch", "put"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_read = False
        instance.save()
        return Response(
            status=status.HTTP_200_OK, data=NotificationSerializer(instance).data
        )


class NotificationMarkAllReadView(APIView):
    """Mark all notifications for the user as read."""

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True
        )
        return Response(
            status=status.HTTP_200_OK,
            data={"message": "All notifications marked as read"},
        )


class NotificationDeleteAllView(APIView):
    """Delete all notifications for the user."""

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        Notification.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationDeleteView(generics.DestroyAPIView):
    """Delete a single notification."""

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
