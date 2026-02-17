# accounts/dashboard.py
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.utils import timezone
from datetime import timedelta
from issues.models import (
    Issue,
    IssueLike,
    IssueComment,
    IssueProgress,
)
from accounts.models import User
from notification.models import Notification
from testimonial.models import Testimonial


def _serialize_issue_short(issue):
    if not issue:
        return None
    return {
        "id": issue.id,
        "title": getattr(issue, "title", ""),
        "created_at": getattr(issue, "created_at", None),
        "reported_by": {
            "id": issue.reported_by.id if getattr(issue, "reported_by", None) else None,
            "email": issue.reported_by.email
            if getattr(issue, "reported_by", None)
            else None,
            "full_name": issue.reported_by.get_full_name()
            if getattr(issue, "reported_by", None)
            else None,
        },
    }


def get_analytics_data(request, context):
    now = timezone.now()

    # Issues
    all_issues = Issue.objects.all()
    total_issues = all_issues.count()
    total_resolved = all_issues.filter(is_resolved=True).count()

    # Average resolution time (days)
    avg_res_time = None
    resolved_issues = all_issues.filter(is_resolved=True)
    if resolved_issues.exists():
        res_data = resolved_issues.annotate(
            res_time=ExpressionWrapper(
                F("resolved_at") - F("created_at"), output_field=DurationField()
            )
        )
        avg_seconds = res_data.aggregate(avg=Avg("res_time"))["avg"]
        if avg_seconds:
            avg_res_time = round(avg_seconds.total_seconds() / 86400, 1)

    # Monthly trends (last 12 months)
    twelve_months_ago = now - timedelta(days=365)
    trend_labels = []
    trend_values = []
    for i in range(12):
        month_start = twelve_months_ago + timedelta(days=30 * i)
        count = all_issues.filter(
            created_at__gte=month_start, created_at__lt=month_start + timedelta(days=30)
        ).count()
        trend_labels.append(month_start.strftime("%b"))
        trend_values.append(count)

    # Category distribution
    category_stats = list(
        all_issues.values("category").annotate(count=Count("id")).order_by("-count")
    )

    # Top reporting user
    top_reporter = (
        User.objects.annotate(report_count=Count("reported_issues"))
        .filter(report_count__gt=0)
        .order_by("-report_count")
        .first()
    )
    top_reporter_summary = None
    if top_reporter:
        last_report = (
            Issue.objects.filter(reported_by=top_reporter)
            .order_by("-created_at")
            .values("id", "title", "created_at")
            .first()
        )
        top_reporter_summary = {
            "id": top_reporter.id,
            "email": top_reporter.email,
            "full_name": top_reporter.get_full_name(),
            "profile_pic": top_reporter.profile_pic.url
            if top_reporter.profile_pic
            else None,
            "report_count": getattr(top_reporter, "report_count", 0),
            "last_report": last_report,
        }

    # Top liked issue (only if there are likes)
    top_liked_issue_obj = (
        Issue.objects.annotate(like_count=Count("likes"))
        .filter(like_count__gt=0)
        .order_by("-like_count")
        .first()
    )
    top_liked_issue = None
    if top_liked_issue_obj:
        top_liked_issue = {
            "id": top_liked_issue_obj.id,
            "title": top_liked_issue_obj.title,
            "like_count": getattr(top_liked_issue_obj, "like_count", 0),
            "reported_by": {
                "id": top_liked_issue_obj.reported_by.id,
                "email": top_liked_issue_obj.reported_by.email,
                "full_name": top_liked_issue_obj.reported_by.get_full_name(),
            },
            "created_at": top_liked_issue_obj.created_at,
        }

    # Users analytics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    new_users_last_30 = User.objects.filter(
        created_at__gte=now - timedelta(days=30)
    ).count()

    # Testimonials analytics
    total_testimonials = Testimonial.objects.count()
    avg_testimonial_rating = (
        Testimonial.objects.aggregate(avg=Avg("rating"))["avg"] or 0
    )
    testimonials_displayed = Testimonial.objects.filter(is_displayed=True).count()

    # Notifications analytics
    total_notifications = Notification.objects.count()
    unread_notifications = Notification.objects.filter(is_read=False).count()

    # Issue progress / comments analytics
    total_progress_updates = IssueProgress.objects.count()
    avg_progress_per_issue = (
        round(total_progress_updates / total_issues, 2) if total_issues else 0
    )

    top_commented_issue_obj = (
        Issue.objects.annotate(comment_count=Count("comments"))
        .filter(comment_count__gt=0)
        .order_by("-comment_count")
        .first()
    )
    top_commented_issue = None
    if top_commented_issue_obj:
        top_commented_issue = {
            "id": top_commented_issue_obj.id,
            "title": top_commented_issue_obj.title,
            "comment_count": getattr(top_commented_issue_obj, "comment_count", 0),
        }

    # Basic totals already present in previous version
    total_likes = IssueLike.objects.count()
    total_comments = IssueComment.objects.count()

    # Status breakdown
    status_breakdown = {
        "resolved": total_resolved,
        "pending": all_issues.filter(is_resolved=False, is_archived=False).count(),
        "archived": all_issues.filter(is_archived=True).count(),
    }

    # Build context (merged with incoming context)
    context.update(
        {
            "total_issues": total_issues,
            "total_resolved": total_resolved,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "res_rate": round((total_resolved / total_issues * 100), 1)
            if total_issues > 0
            else 0,
            "avg_res_time": avg_res_time or "N/A",
            "trend_labels": trend_labels,
            "trend_values": trend_values,
            "category_labels": [c["category"] for c in category_stats],
            "category_values": [c["count"] for c in category_stats],
            "status_breakdown": status_breakdown,
            # new keys
            "top_reporter": top_reporter_summary,
            "top_liked_issue": top_liked_issue,
            "users_total": total_users,
            "users_active": active_users,
            "users_new_30": new_users_last_30,
            "testimonials_total": total_testimonials,
            "testimonials_avg_rating": round(avg_testimonial_rating, 2),
            "testimonials_displayed": testimonials_displayed,
            "notifications_total": total_notifications,
            "notifications_unread": unread_notifications,
            "progress_total": total_progress_updates,
            "progress_avg_per_issue": avg_progress_per_issue,
            "top_commented_issue": top_commented_issue,
        }
    )

    return context
