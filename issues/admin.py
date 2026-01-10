from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Issue, IssueComment, IssueImage, IssueLike, IssueProgress, IssueProgressImage, IssueCategory

class IssueImageInline(admin.TabularInline):
    model = IssueImage
    extra = 1
    readonly_fields = ["image_preview"]

    @admin.display(description=_("Preview"))
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:100px; border-radius:4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.image.url,
            )
        return "-"

class IssueCommentInline(admin.TabularInline):
    model = IssueComment
    extra = 0
    readonly_fields = ["created_at", "updated_at"]
    fields = ["commented_by", "text", "created_at"]

class IssueLikeInline(admin.TabularInline):
    model = IssueLike
    extra = 0
    readonly_fields = ["created_at"]
    fields = ["liked_by", "created_at"]

class IssueProgressImageInline(admin.TabularInline):
    model = IssueProgressImage
    extra = 1

class IssueProgressInline(admin.StackedInline):
    model = IssueProgress
    extra = 0
    fields = ["title", "description", "updated_by"]
    autocomplete_fields = ["updated_by"]

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "display_title",
        "status_badge",
        "category_badge",
        "reported_by",
        "created_at",
        "stats_summary"
    ]
    list_filter = ["is_resolved", "is_archived", "category", "created_at"]
    search_fields = ["title", "description", "reported_by__email", "reported_by__first_name"]
    autocomplete_fields = ["reported_by"]
    inlines = [IssueImageInline, IssueProgressInline, IssueCommentInline, IssueLikeInline]
    readonly_fields = ["created_at", "updated_at"]
    
    list_display_links = ["id", "display_title"]

    fieldsets = (
        (_("Basic Information"), {
            "fields": (("title", "category"), "description")
        }),
        (_("Status & Archiving"), {
            "fields": (("is_resolved", "is_archived"),)
        }),
        (_("Location Details"), {
            "fields": ("address", ("latitude", "longitude")),
            "classes": ["collapse"]
        }),
        (_("Reporter Info"), {
            "fields": ("reported_by",),
            "classes": ["collapse"]
        }),
    )

    actions = ["mark_as_resolved", "archive_issues", "unarchive_issues"]

    @admin.display(description=_("Title"))
    def display_title(self, obj):
        return obj.title

    @admin.display(description=_("Status"))
    def status_badge(self, obj):
        if obj.is_resolved:
            return format_html(
                '<span style="padding: 2px 8px; border-radius: 12px; background: #dcfce7; color: #15803d; font-size: 11px; font-weight: bold;">{}</span>',
                _("Resolved")
            )
        if obj.is_archived:
            return format_html(
                '<span style="padding: 2px 8px; border-radius: 12px; background: #f3f4f6; color: #374151; font-size: 11px; font-weight: bold;">{}</span>',
                _("Archived")
            )
        return format_html(
            '<span style="padding: 2px 8px; border-radius: 12px; background: #dbeafe; color: #1d4ed8; font-size: 11px; font-weight: bold;">{}</span>',
            _("Open")
        )

    @admin.display(description=_("Category"))
    def category_badge(self, obj):
        return format_html(
            '<span style="padding: 2px 6px; border-radius: 4px; background: #f3f0ff; color: #6b21a8; font-size: 11px; font-weight: 500; border: 1px solid #e9d5ff;">{}</span>',
            obj.category.upper()
        )

    @admin.display(description=_("Stats"))
    def stats_summary(self, obj):
        return format_html(
            '<div style="display: flex; gap: 10px; color: #6b7280; font-size: 12px;">'
            '<span>🖼️ {}</span>'
            '<span>💬 {}</span>'
            '<span>❤️ {}</span>'
            '</div>',
            obj.images.count(),
            obj.comments.count(),
            obj.likes.count()
        )

    @admin.action(description=_("Mark selected issues as resolved"))
    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
        self.message_user(request, _("Selected issues have been marked as resolved."), messages.SUCCESS)

    @admin.action(description=_("Archive selected issues"))
    def archive_issues(self, request, queryset):
        queryset.update(is_archived=True)
        self.message_user(request, _("Selected issues have been archived."), messages.SUCCESS)

    @admin.action(description=_("Unarchive selected issues"))
    def unarchive_issues(self, request, queryset):
        queryset.update(is_archived=False)
        self.message_user(request, _("Selected issues have been unarchived."), messages.SUCCESS)

@admin.register(IssueComment)
class IssueCommentAdmin(admin.ModelAdmin):
    list_display = ["id", "issue_link", "commented_by", "short_text", "created_at"]
    search_fields = ["text", "commented_by__email", "issue__title"]
    autocomplete_fields = ["issue", "commented_by"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at", "updated_at"]

    @admin.display(description=_("Issue"))
    def issue_link(self, obj):
        return obj.issue.title

    @admin.display(description=_("Text"))
    def short_text(self, obj):
        return (obj.text[:50] + '...') if len(obj.text) > 50 else obj.text

@admin.register(IssueCategory)
class IssueCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]

@admin.register(IssueProgress)
class IssueProgressAdmin(admin.ModelAdmin):
    list_display = ["title", "issue", "updated_by", "created_at"]
    autocomplete_fields = ["issue", "updated_by"]
    inlines = [IssueProgressImageInline]

@admin.register(IssueImage)
class IssueImageAdmin(admin.ModelAdmin):
    list_display = ["id", "issue_link", "image_preview", "created_at"]
    search_fields = ["issue__title"]
    readonly_fields = ["created_at", "updated_at", "image_preview"]

    @admin.display(description=_("Issue"))
    def issue_link(self, obj):
        return obj.issue.title

    @admin.display(description=_("Preview"))
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; border-radius:4px;" />',
                obj.image.url,
            )
        return "-"

@admin.register(IssueLike)
class IssueLikeAdmin(admin.ModelAdmin):
    list_display = ["id", "issue_link", "liked_by", "created_at"]
    search_fields = ["issue__title", "liked_by__email"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at", "updated_at"]

    @admin.display(description=_("Issue"))
    def issue_link(self, obj):
        return obj.issue.title
