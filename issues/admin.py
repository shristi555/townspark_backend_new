
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Issue, IssueComment, IssueImage, IssueLike

"""
We are using django-unfold for a better admin interface.
Refer: https://django-unfold.readthedocs.io/en/latest/
"""

class IssueImageInline(TabularInline):
    model = IssueImage
    extra = 1
    tab = True
    readonly_fields = ["image_preview"]

    @display(description="Preview")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:100px; border-radius:4px;" />',
                obj.image.url,
            )
        return "-"

class IssueCommentInline(TabularInline):
    model = IssueComment
    extra = 0
    tab = True
    readonly_fields = ["created_at", "updated_at"]
    fields = ["commented_by", "text", "created_at"]

class IssueLikeInline(TabularInline):
    model = IssueLike
    extra = 0
    tab = True
    readonly_fields = ["created_at"]
    fields = ["liked_by", "created_at"]
@admin.register(Issue)
class IssueAdmin(ModelAdmin):
    list_display = [
        "id",
        "title",
        "category",
        "reported_by",
        "is_resolved",
        "created_at",
        "image_count",
        "comment_count",
        "like_count"
    ]
    list_filter = ["is_resolved", "category", "created_at"]
    search_fields = ["title", "description", "reported_by__email", "reported_by__first_name"]
    inlines = [IssueImageInline, IssueCommentInline, IssueLikeInline]
    readonly_fields = ["created_at", "updated_at"]
    
    list_display_links = ["id","title"]

    fieldsets = (
        (None, {
            "fields": ("title", "description", "category", "is_resolved")
        }),
        ("Reporter Info", {
            "fields": ("reported_by",),
            "classes": ["collapse"]
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ["collapse"]
        }),
    )

    def get_change_form_template(self, request, obj=None, **kwargs):
        """
        Override the change form template to show the custom details page
        only when viewing an existing issue (obj is not None).
        """
        if obj:
            return "admin/issues/issue/change_form.html"
        return super().get_change_form_template(request, obj, **kwargs)

    @display(description="Images")
    def image_count(self, obj):
        return obj.images.count()

    @display(description="Comments")
    def comment_count(self, obj):
        return obj.comments.count()

    @display(description="Likes")
    def like_count(self, obj):
        return obj.likes.count()

@admin.register(IssueComment)
class IssueCommentAdmin(ModelAdmin):
    list_display = ["id", "issue_link", "commented_by", "short_text", "created_at"]
    search_fields = ["text", "commented_by__email", "issue__title"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at", "updated_at"]

    @display(description="Issue")
    def issue_link(self, obj):
        return obj.issue.title

    @display(description="Text")
    def short_text(self, obj):
        return (obj.text[:50] + '...') if len(obj.text) > 50 else obj.text

@admin.register(IssueImage)
class IssueImageAdmin(ModelAdmin):
    list_display = ["id", "issue_link", "image_preview", "created_at"]
    search_fields = ["issue__title"]
    readonly_fields = ["created_at", "updated_at", "image_preview"]

    @display(description="Issue")
    def issue_link(self, obj):
        return obj.issue.title

    @display(description="Preview")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; border-radius:4px;" />',
                obj.image.url,
            )
        return "-"

@admin.register(IssueLike)
class IssueLikeAdmin(ModelAdmin):
    list_display = ["id", "issue_link", "liked_by", "created_at"]
    search_fields = ["issue__title", "liked_by__email"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at", "updated_at"]

    @display(description="Issue")
    def issue_link(self, obj):
        return obj.issue.title