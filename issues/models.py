from django.db import models
from uuid import uuid4


def issue_image_upload_path(instance, filename):
    """Generate upload path for issue images."""
    ext = filename.split(".")[-1]
    return f"issue_images/{instance.issue.id}/{uuid4().hex}.{ext}"


def progress_image_upload_path(instance, filename):
    """Generate upload path for progress images."""
    ext = filename.split(".")[-1]
    return f"progress_images/{instance.progress.issue.id}/{instance.progress.id}/{uuid4().hex}.{ext}"


class BaseTimedModel(models.Model):
    """Abstract base model with timestamp fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class IssueCategory(models.Model):
    """Categories for classifying issues (e.g., Pothole, Street Light)."""

    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Issue Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Issue(BaseTimedModel):
    """Main issue model representing community problems."""

    title = models.CharField(max_length=255)
    description = models.TextField()

    # Status fields
    is_resolved = models.BooleanField(default=False, db_index=True)
    is_archived = models.BooleanField(default=False, db_index=True)

    # Category
    # category = models.ForeignKey(
    #     IssueCategory,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="issues",  # Access via: category.issues.all()
    #     help_text="Category of the issue",
    # )

    # for now category is charfield to simplify category management
    category = models.CharField(
        max_length=100, blank=True, default="general", db_index=True
    )

    # User relationship
    reported_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="reported_issues",  # Access via: user.reported_issues.all()
        help_text="User who reported this issue",
    )

    # Location fields
    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(
        max_digits=13, decimal_places=10, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=13, decimal_places=10, null=True, blank=True
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_resolved", "is_archived", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.title} (#{self.id})"

    @property
    def like_count(self):
        """Return the number of likes for this issue."""
        return self.likes.count()

    @property
    def comment_count(self):
        """Return the number of comments for this issue."""
        return self.comments.count()


class IssueComment(BaseTimedModel):
    """Comments on issues."""

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="comments",  # Access via: issue.comments.all()
    )
    text = models.TextField()
    commented_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="issue_comments",  # Access via: user.issue_comments.all()
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["issue", "created_at"]),
        ]

    def __str__(self):
        return f"Comment by {self.commented_by.email} on {self.issue.title}"


class IssueImage(BaseTimedModel):
    """Images attached to issues."""

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="images",  # Access via: issue.images.all()
    )
    image = models.ImageField(upload_to=issue_image_upload_path)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Image for Issue #{self.issue.id}"


class IssueLike(BaseTimedModel):
    """Track user likes on issues (one like per user per issue)."""

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="likes",  # Access via: issue.likes.all()
    )
    liked_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="liked_issues",  # Access via: user.liked_issues.all()
    )

    class Meta:
        unique_together = ("issue", "liked_by")
        indexes = [
            models.Index(fields=["issue"]),
            models.Index(fields=["liked_by"]),
        ]

    def __str__(self):
        return f"{self.liked_by.email} liked Issue #{self.issue.id}"


class IssueProgress(BaseTimedModel):
    """
    Progress updates for issues (immutable once created).
    Tracks status changes like 'Investigation Started', 'Fix Deployed', etc.
    """

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="progress_updates",  # Access via: issue.progress_updates.all()
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    updated_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="issue_progress_updates",  # Access via: user.issue_progress_updates.all()
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Issue Progress Updates"

    def __str__(self):
        return f"{self.title} - Issue #{self.issue.id}"

    @property
    def image_count(self):
        """Return the number of images for this progress update."""
        return self.images.count()


class IssueProgressImage(BaseTimedModel):
    """Images attached to progress updates."""

    progress = models.ForeignKey(
        IssueProgress,
        on_delete=models.CASCADE,
        related_name="images",  # Access via: progress.images.all()
    )
    image = models.ImageField(upload_to=progress_image_upload_path)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Image for Progress #{self.progress.id}"
