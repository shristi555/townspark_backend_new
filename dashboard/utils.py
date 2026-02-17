# accounts/dashboard.py
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.utils import timezone
from datetime import timedelta
from issues.models import Issue, IssueLike, IssueComment  # adjust imports as needed


def get_analytics_data(request, context):
    all_issues = Issue.objects.all()
    now = timezone.now()

    # --- Basic Counts ---
    total_issues = all_issues.count()
    total_resolved = all_issues.filter(is_resolved=True).count()

    # --- Resolution Stats ---
    resolved_issues = all_issues.filter(is_resolved=True)
    avg_res_time = None
    if resolved_issues.exists():
        res_data = resolved_issues.annotate(
            res_time=ExpressionWrapper(
                F("resolved_at") - F("created_at"), output_field=DurationField()
            )
        )
        avg_seconds = res_data.aggregate(avg=Avg("res_time"))["avg"]
        if avg_seconds:
            avg_res_time = round(avg_seconds.total_seconds() / 86400, 1)

    # --- Monthly Trends (Line Chart) ---
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

    # --- Category Distribution (Pie Chart) ---
    category_stats = list(
        all_issues.values("category").annotate(count=Count("id")).order_by("-count")
    )

    # Update context with everything your template needs
    context.update(
        {
            "total_issues": total_issues,
            "total_resolved": total_resolved,
            "total_likes": IssueLike.objects.count(),
            "total_comments": IssueComment.objects.count(),
            "res_rate": round((total_resolved / total_issues * 100), 1)
            if total_issues > 0
            else 0,
            "avg_res_time": avg_res_time or "N/A",
            "trend_labels": trend_labels,
            "trend_values": trend_values,
            "category_labels": [c["category"] for c in category_stats],
            "category_values": [c["count"] for c in category_stats],
            "status_breakdown": {
                "resolved": total_resolved,
                "pending": all_issues.filter(
                    is_resolved=False, is_archived=False
                ).count(),
                "archived": all_issues.filter(is_archived=True).count(),
            },
        }
    )
    return context
