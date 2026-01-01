from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationViewSet, 
    NotificationReadView, 
    NotificationUnreadView, 
    NotificationMarkAllReadView, 
    NotificationDeleteAllView,
    NotificationDeleteView
)

router = DefaultRouter()
router.register(r'', NotificationViewSet, basename='notification')

urlpatterns = [
    path('read/<int:pk>/', NotificationReadView.as_view(), name='notification-read'),
    path('unread/<int:pk>/', NotificationUnreadView.as_view(), name='notification-unread'),
    path('mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('delete-all/', NotificationDeleteAllView.as_view(), name='notification-delete-all'),
    path('delete/<int:pk>/', NotificationDeleteView.as_view(), name='notification-delete'),
    path('', include(router.urls)),
]
