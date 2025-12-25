from django.contrib import admin
from django.utils.html import format_html
from accounts.models import User


# Admin site branding
admin.site.site_header = "Townspark Administration"
admin.site.site_title = "Townspark Admin"
admin.site.index_title = "Site Administration"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
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

    # Human\-readable full name column
    def full_name_display(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    full_name_display.short_description = "Full name"

    # Small profile picture preview in admin
    def profile_pic_tag(self, obj):
        if obj.profile_pic:
            return format_html(
                '<img src="{}" style="max-height:75px; border-radius:4px;" />',
                obj.profile_pic.url,
            )
        return "-"

    profile_pic_tag.short_description = "Profile pic"
