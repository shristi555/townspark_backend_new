from django.contrib import admin
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ["user", "rating", "designation", "is_displayed", "created_at"]
    list_filter = ["rating", "is_displayed", "created_at"]
    search_fields = ["user__email", "feedback", "designation"]
    list_editable = ["is_displayed"]
    autocomplete_fields = ["user"]
