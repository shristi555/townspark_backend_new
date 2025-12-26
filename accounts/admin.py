from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display
from accounts.models import User


"""
TODO: Customize the admin interface using django-unfold for better usability.
"""


# Admin site branding
admin.site.site_header = "Townspark Administration"
admin.site.site_title = "Townspark Admin"
admin.site.index_title = "Site Administration"


@admin.register(User)
class UserAdmin(ModelAdmin):
    model = User

    # Columns shown in the changelist
    list_display = (
        "id",
        "email",
        "full_name_display",
        "phone_number",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
    )

    search_fields = ("email", "first_name", "last_name", "phone_number")
    list_filter = ("is_active", "is_staff", "is_superuser")
    ordering = ("email",)

    # Do not show password; make created_at and the profile preview readonly
    exclude = ("password",)
    readonly_fields = ("created_at", "profile_pic_tag")

    # Organize fields in the change form
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "full_name_display",
                    "phone_number",
                    "profile_pic_tag",
                    "profile_pic",
                )
            },
        ),
        (
            "Permissions",
            {
                "classes": ["collapse"],
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )

    # Human-readable full name column
    @display(description="Full name")
    def full_name_display(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    # Small profile picture preview in admin
    @display(description="Profile pic")
    def profile_pic_tag(self, obj):
        if obj.profile_pic:
            return format_html(
                '<img src="{}" width="75" height="75" style="max-height:75px; border-radius:4px;" />',
                obj.profile_pic.url,
            )
        return "-"
