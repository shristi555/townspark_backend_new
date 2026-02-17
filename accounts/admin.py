from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.conf import settings
from unfold.admin import ModelAdmin
from unfold.decorators import display
from accounts.models import User


class UserListMixin:
    """Handles all logic for the User Table / List View"""

    list_display = [
        "display_header",
        "display_phone",
        "display_status",
        "created_at",
        "display_actions",
    ]

    empty_value_display = "--"

    @display(description="User", header=False)  # Changed to False to take full control
    def display_header(self, instance):
        full_name = instance.get_full_name() or "No Name"

        # 1. Create the Avatar (Image or Initials)
        if instance.profile_pic:
            # THere is  need to display the initials for some days in this server
            # i will revert to img in future
            avatar_html = format_html(
                '<div class="w-10 h-10 rounded-full bg-primary-600 text-white flex items-center justify-center font-bold text-xs p-2">{}</div>',
                instance.initials,
            )
        else:
            initials = (
                instance.first_name[0] if instance.first_name else instance.email[0]
            ).upper()
            avatar_html = format_html(
                '<div class="w-10 h-10 rounded-full bg-primary-600 text-white flex items-center justify-center font-bold text-xs">{}</div>',
                initials,
            )

        # 2. Return a SINGLE format_html block.
        # This bypasses Unfold's "list of 3" requirement and guarantees it looks like a modern row.
        return format_html(
            '<div class="flex items-center gap-x-3 text-left">'
            "   {}"
            '   <div class="flex flex-col">'
            '       <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">{}</span>'
            '       <span class="text-xs text-gray-500 font-normal">{}</span>'
            "   </div>"
            "</div>",
            avatar_html,
            full_name,
            instance.email,
        )

    # ... keep the rest of your display_status, display_phone, and display_actions ...
    @display(description="Status", label={True: "success", False: "danger"})
    def display_status(self, instance):
        return instance.is_active, "Active" if instance.is_active else "Inactive"

    @display(description="Phone Number")
    def display_phone(self, instance):
        return instance.phone_number or "--"

    @display(description="Actions")
    def display_actions(self, instance):
        change_url = reverse("admin:accounts_user_change", args=[instance.pk])
        return format_html(
            '<div class="flex items-center gap-x-3">'
            '<a href="{}" class="text-gray-400 hover:text-primary-600 transition-colors">'
            '<span class="material-symbols-outlined !text-xl">edit</span></a>'
            '<a href="{}" class="text-gray-400 hover:text-blue-500 transition-colors">'
            '<span class="material-symbols-outlined !text-xl">visibility</span></a>'
            "</div>",
            change_url,
            change_url,
        )


class UserEditMixin:
    """Handles all logic for the User Change Form / Profile View"""

    def display_profile_header(self, instance):
        if not instance.pk:
            return "New User Profile"

        # Big Profile Header UI
        if instance.profile_pic:
            img_tag = format_html(
                '<img src="{}" class="w-32 h-32 rounded-full object-cover border-4 border-white shadow-lg" />',
                instance.profile_pic_absolute_url,
            )
        else:
            img_tag = format_html(
                '<div class="w-32 h-32 rounded-full bg-primary-600 text-white flex items-center justify-center text-4xl font-bold shadow-lg">{}</div>',
                instance.initials,
            )

        return format_html(
            '<div class="flex flex-col items-center justify-center w-full py-10 bg-gray-50 dark:bg-gray-800/50 rounded-2xl border border-dashed border-gray-300 dark:border-gray-700 mb-8">'
            '   <div class="relative group">{}'
            '       <div class="absolute inset-0 bg-black/20 rounded-full opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity cursor-pointer">'
            '           <span class="material-symbols-outlined text-white text-3xl">photo_camera</span>'
            "       </div>"
            "   </div>"
            '   <h2 class="mt-4 text-2xl font-bold text-gray-900 dark:text-white">{}</h2>'
            '   <p class="text-sm text-gray-500 font-medium">{}</p>'
            "</div>",
            img_tag,
            instance.get_full_name() or "New User",
            f"Member since {instance.created_at.strftime('%B %Y')}"
            if instance.created_at
            else "Account pending",
        )

    display_profile_header.short_description = "Profile Overview"


# ==========================================
# 3. FINAL ADMIN ASSEMBLY
# ==========================================
@admin.register(User)
class UserAdmin(UserListMixin, UserEditMixin, ModelAdmin):
    """
    Modular User Admin inheriting List and Edit Mixins.
    """

    # Define which fields are read-only in the edit form
    readonly_fields = ["display_profile_header", "password", "created_at"]

    # Define the actual form layout
    fieldsets = (
        (
            None,
            {
                "fields": ["display_profile_header", "profile_pic"],
            },
        ),
        (
            "Identity Info",
            {
                "fields": (("first_name", "last_name"), "email", "phone_number"),
            },
        ),
        (
            "Access Roles",
            {
                "fields": ("is_active", "is_staff", "is_superuser"),
                "description": "Control user status and administrative access.",
            },
        ),
    )

    # Optional: ensure we can still search and filter
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("is_active", "is_staff")
