from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ("user", "rating", "designation", "is_displayed", "created_at")
    search_fields = ("user__email", "feedback", "designation")
    list_filter = ("rating", "is_displayed")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
