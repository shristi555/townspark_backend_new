from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (
    Issue,
    IssueComment,
    IssueImage,
    IssueLike,
    IssueProgress,
    IssueProgressImage,
    IssueCategory,
)


@admin.register(Issue)
class IssueAdmin(ModelAdmin):
    list_display = (
        "id",
        "title",
        "reported_by",
        "category",
        "is_resolved",
        "is_archived",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "reported_by__email",
        "category",
        "address",
        "city",
    )
    list_filter = ("is_resolved", "is_archived", "category", "city")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(IssueComment)
class IssueCommentAdmin(ModelAdmin):
    list_display = ("issue", "commented_by", "created_at")
    search_fields = ("text", "commented_by__email")
    list_filter = ("issue",)


@admin.register(IssueImage)
class IssueImageAdmin(ModelAdmin):
    list_display = ("issue", "image", "created_at")
    search_fields = ("issue__title",)


@admin.register(IssueLike)
class IssueLikeAdmin(ModelAdmin):
    list_display = ("issue", "liked_by", "created_at")
    search_fields = ("liked_by__email", "issue__title")


@admin.register(IssueProgress)
class IssueProgressAdmin(ModelAdmin):
    list_display = ("issue", "title", "updated_by", "created_at")
    search_fields = ("title", "description", "updated_by__email")


@admin.register(IssueProgressImage)
class IssueProgressImageAdmin(ModelAdmin):
    list_display = ("progress", "image", "created_at")


@admin.register(IssueCategory)
class IssueCategoryAdmin(ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    ordering = ("name",)
