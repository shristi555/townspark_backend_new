from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from accounts.models import User

from django.utils.safestring import mark_safe

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Columns shown in the changelist
    list_display = (
        "id",
        "profile_pic_tag",
        "email",
        "full_name_display",
        "phone_number",
        "status_badges",
        "created_at",
    )

    search_fields = ("email", "first_name", "last_name", "phone_number")
    list_filter = ("is_active", "is_staff", "is_superuser")
    ordering = ("-created_at",)

    # Restrict editing sensitive fields
    readonly_fields = ("email", "last_login", "created_at", "profile_pic_tag")
    exclude = ("password",)

    # Organize fields in the change form
    fieldsets = (
        (_("Identity"), {
            "fields": (
                "profile_pic_tag",
                "profile_pic",
                "email",
                ("first_name", "last_name"),
                "phone_number",
            )
        }),
        (_("Roles & Permissions"), {
            "fields": (
                ("is_active", "is_staff", "is_superuser"),
                "groups",
                "user_permissions",
            ),
            "classes": ["collapse"],
        }),
        (_("Important Dates"), {
            "fields": (("last_login", "created_at"),),
            "classes": ["collapse"],
        }),
    )

    @admin.display(description=_("Full Name"))
    def full_name_display(self, obj):
        return f"{obj.first_name} {obj.last_name or ''}".strip() or "---"

    @admin.display(description=_("Status"))
    def status_badges(self, obj):
        badges = []
        if obj.is_superuser:
            badges.append('<span style="padding: 2px 6px; border-radius: 10px; background: #fee2e2; color: #991b1b; font-size: 10px; font-weight: bold; margin-right: 4px;">SUPERUSER</span>')
        elif obj.is_staff:
            badges.append('<span style="padding: 2px 6px; border-radius: 10px; background: #dbeafe; color: #1e40af; font-size: 10px; font-weight: bold; margin-right: 4px;">STAFF</span>')
        
        if obj.is_active:
            badges.append('<span style="padding: 2px 6px; border-radius: 10px; background: #dcfce7; color: #166534; font-size: 10px; font-weight: bold;">ACTIVE</span>')
        else:
            badges.append('<span style="padding: 2px 6px; border-radius: 10px; background: #f3f4f6; color: #374151; font-size: 10px; font-weight: bold;">INACTIVE</span>')
        
        return format_html('<div style="display: flex;">{}</div>', mark_safe("".join(badges)))

    @admin.display(description=_("Profile"))
    def profile_pic_tag(self, obj):
        if obj.profile_pic:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 2px solid #e5e7eb;" />',
                obj.profile_pic.url,
            )
        return format_html(
            '<div style="width: 40px; height: 40px; border-radius: 50%; background: #ddd6fe; display: flex; align-items: center; justify-content: center; color: #5b21b6; font-weight: bold;">{}</div>',
            obj.first_name[0].upper() if obj.first_name else "?"
        )
