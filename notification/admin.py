from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ("title", "user", "event", "is_read", "created_at")
    search_fields = ("title", "description", "event", "user__email")
    list_filter = ("is_read", "event")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
