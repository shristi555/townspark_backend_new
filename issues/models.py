from django.db import models
from uuid import uuid4

"""
For simplicity, we will keep all issue related models in this single file.
I dont wanna change the directory structure too much for now.
In future, if the models grow too much we can split them into multiple files.
"""


def issue_image_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"issue_images/{instance.issue_id}/{uuid4().hex}.{ext}"


# Create your models here.
class BaseTimedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Issue(BaseTimedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_resolved = models.BooleanField(default=False, blank=True, db_index=True)

    # for now the issue catregory will be a simple char field
    # but in future we will make it a foreign key to a separate IssueCategory model
    category = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    # this will be a foreign key to the user model in accounts app
    reported_by = models.ForeignKey(
        "accounts.User", related_name="reported_issues", on_delete=models.CASCADE
    )

    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title


# seperate tables for those items that can have multiple entries per issue
class IssueComment(BaseTimedModel):
    # the issue on which the comment is made
    issue = models.ForeignKey(Issue, related_name="comments", on_delete=models.CASCADE)

    # the actual comment text
    text = models.TextField()

    commented_by = models.ForeignKey(
        "accounts.User", related_name="issue_comments", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment on {self.issue.title} at {self.created_at}"


class IssueImage(BaseTimedModel):
    """
    We will store the images in a media folder as below
    <media>/issue_images/<issue_id>/<image_number>.<extension>

    1. issue_id will be the id of the issue to which the image belongs
    2. image_number will be a sequential number for each image of the issue
    no matter what the image is named when uploaded we will rename it to image_1, image_2 etc
    3. extension will be the original extension of the uploaded image
    4. We will create a function to handle the upload path
    """

    issue = models.ForeignKey(Issue, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=issue_image_upload_path)

    def __str__(self):
        return f"Image for {self.issue.title} at {self.created_at}"


class IssueLike(BaseTimedModel):
    issue = models.ForeignKey(Issue, related_name="likes", on_delete=models.CASCADE)
    liked_by = models.ForeignKey(
        "accounts.User", related_name="liked_issues", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("issue", "liked_by")
        indexes = [
            models.Index(fields=["issue"]),
            models.Index(fields=["liked_by"]),
        ]

    def __str__(self):
        return f"{self.liked_by.email} liked {self.issue.title}"


class IssueProgress(BaseTimedModel):
    """
    Model to track the progress of an issue.

    it will store the following information:
    1. issue - foreign key to the issue
    2. Title - title of the issue progress (e.g "Investigation Started", "Fix Deployed" etc)
    3. Description - description of the issue progress (e.g "We have started investigating the issue" etc)
    4. updated_by - foreign key to the user who updated the progress (e.g most likely the admin user or the one who uploaded the issue)
    5. timestamp - timestamp of when the progress was updated (auto set to now on creation)
    6. created_at - timestamp of when the progress was created (auto set to now on creation)
    progress updates will not be editable or deletable once created.

    """

    issue = models.ForeignKey(
        Issue, related_name="progress_updates", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    updated_by = models.ForeignKey(
        "accounts.User", related_name="issue_progress_updates", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Progress Update: {self.title} for {self.issue.title} at {self.created_at}"
        )


class IssueCategory(models.Model):
    """
    Model to represent issue categories.
    it is used to categorize issues into different types.
    e.g "Pothole", "Street Light", "Garbage", "Water Leakage" etc

    it will also be helpful in filtering issues based on category.

    fields:
    1. id - primary key
    2. name - name of the category (e.g "Pothole", "Street Light", "Garbage", "Water Leakage" etc)
    3. description - description of the category on what it should be used for

    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Issue Categories"
        ordering = ["name"]
