from django.contrib import admin
from django.utils.html import format_html
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "event", "read_status", "created_at"]
    list_filter = ["event", "is_read", "created_at"]
    search_fields = ["title", "description", "user__email"]
    readonly_fields = ["created_at"]
    autocomplete_fields = ["user"]

    @admin.display(description="Status")
    def read_status(self, obj):
        if obj.is_read:
            return format_html(
                '<span style="padding: 2px 8px; border-radius: 12px; background: #dcfce7; color: #15803d; font-size: 11px; font-weight: bold;">Read</span>'
            )
        return format_html(
            '<span style="padding: 2px 8px; border-radius: 12px; background: #fee2e2; color: #b91c1c; font-size: 11px; font-weight: bold;">Unread</span>'
        )
