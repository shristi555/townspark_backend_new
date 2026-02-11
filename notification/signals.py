from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import Notification
from issues.models import Issue, IssueProgress

User = settings.AUTH_USER_MODEL

# User Signals

@receiver(pre_save, sender=User)
def track_user_changes(sender, instance, **kwargs):
    """
    Track changes to user fields before saving.
    """
    if instance.pk:
        try:
            old_instance = sender._default_manager.get(pk=instance.pk)
            instance._old_profile_pic = old_instance.profile_pic
        except sender.DoesNotExist:
            pass

@receiver(post_save, sender=User)
def user_activity(sender, instance, created, **kwargs):
    """
    Create notifications for user creation and updates.
    """
    if created:
        Notification.objects.create(
            user=instance,
            event="user_created",
            title="Welcome to TownSpark!",
            description="Your account has been successfully created."
        )
    else:
        # Check specific changes
        if hasattr(instance, '_old_profile_pic') and instance.profile_pic != instance._old_profile_pic:
            Notification.objects.create(
                user=instance,
                event="user_updated",
                title="user profile pic changed",
                description="Your profile picture has been updated."
            )
        else:
            # Generic update
            # We assume any other save is an update. 
            # Note: This might be noisy, so we might want to check if ANY relevant field changed.
            # For now, following prompt "user_updated" logic.
            Notification.objects.create(
                user=instance,
                event="user_updated",
                title="Profile Updated",
                description="Your profile details have been updated."
            )

@receiver(post_delete, sender=User)
def user_deleted(sender, instance, **kwargs):
    """
    Log user deletion. Note: The user won't see this as they are deleted, 
    but it serves as a log if the Notification model outlives the User (e.g. if we change on_delete).
    Currently Notification user is CASCADE, so this is just for compliance with prompt 'user deleted'.
    """
    # If we had a log system, we'd log here. 
    # Since we can't create a notification linked to a deleted user (ConstraintError), 
    # we skip DB creation here unless we have a separate generic log or admin notification.
    pass


# Issue Signals 

@receiver(pre_save, sender=Issue)
def track_issue_changes(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Issue.objects.get(pk=instance.pk)
            instance._old_is_resolved = old_instance.is_resolved
            instance._old_is_archived = old_instance.is_archived
        except Issue.DoesNotExist:
            pass

@receiver(post_save, sender=Issue)
def issue_activity(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.reported_by,
            event="issue_created",
            title="New Issue Posting",
            description=f"You reported a new issue: {instance.title}",
            related_id=instance.id
        )
    else:
        # Check specific status changes
        if hasattr(instance, '_old_is_resolved') and instance.is_resolved and not instance._old_is_resolved:
            Notification.objects.create(
                user=instance.reported_by,
                event="issue_resolved",
                title="Issue Resolved",
                description=f"Your issue '{instance.title}' has been marked as resolved.",
                related_id=instance.id
            )
        elif hasattr(instance, '_old_is_archived') and instance.is_archived and not instance._old_is_archived:
            Notification.objects.create(
                user=instance.reported_by,
                event="issue_archived",
                title="Issue Archived",
                description=f"Your issue '{instance.title}' has been archived.",
                related_id=instance.id
            )
        else:
             Notification.objects.create(
                user=instance.reported_by,
                event="issue_updated",
                title="Issue Updated",
                description=f"Your issue '{instance.title}' has been updated.",
                related_id=instance.id
            )

# Issue Progress Signals

@receiver(post_save, sender=IssueProgress)
def issue_progress_activity(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.issue.reported_by,
            event="issue_progress_updated",
            title="Wait for Update", # Or "Progress Update"
            description=f"New progress on issue '{instance.issue.title}': {instance.title}",
            related_id=instance.id
        )
