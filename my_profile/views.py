from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.utils import timezone
from datetime import timedelta
from accounts.serializers import UserSerializer
from issues.serializers import IssueListSerializer
from accounts.models import User
from issues.models import Issue, IssueComment, IssueLike


class GetProfileInfoView(APIView):
    """
    Retrieve the profile information of the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response(
                {"error": "You are not logged in or your session has expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Get user info
        user_info = user.get_user_info()

        # Get reported issues
        reported_issues = user.reported_issues.all().order_by("-created_at")
        reported_issues_serializer = IssueListSerializer(reported_issues, many=True)

        # Get liked issues
        liked_issues = Issue.objects.filter(likes__liked_by=user).order_by(
            "-created_at"
        )
        liked_issues_serializer = IssueListSerializer(liked_issues, many=True)

        # Get commented issues with user's comments
        commented_issues = (
            Issue.objects.filter(comments__commented_by=user)
            .distinct()
            .order_by("-created_at")
        )

        commented_issues_data = []
        for issue in commented_issues:
            issue_data = IssueListSerializer(issue).data
            # Get all comments by this user on this issue
            user_comments = issue.comments.filter(commented_by=user).values(
                "id", "text", "created_at"
            )
            issue_data["user_comments"] = list(user_comments)
            commented_issues_data.append(issue_data)

        # Calculate stats
        total_comments_made = IssueComment.objects.filter(commented_by=user).count()

        # Calculate impact rank
        user_issue_count = user.reported_issues.count()
        impact_rank = User.objects.annotate(
            issue_count=Count('reported_issues')
        ).filter(issue_count__gt=user_issue_count).count() + 1

        # Resolution overview (last 7 days)
        resolution_overview = []
        for i in range(7):
            date = (timezone.now() - timedelta(days=6-i)).date()
            resolved_count = user.reported_issues.filter(
                is_resolved=True, 
                resolved_at__date=date
            ).count()
            reported_count = user.reported_issues.filter(
                created_at__date=date
            ).count()
            resolution_overview.append({
                "day": date.strftime("%a"),
                "resolved": resolved_count,
                "reported": reported_count,
            })

        # Category breakdown for this user
        category_breakdown = list(user.reported_issues.values('category').annotate(count=Count('id')).order_by('-count'))

        response_data = {
            "user": user_info,
            "reported_issues": {
                "count": reported_issues.count(),
                "issues": reported_issues_serializer.data,
            },
            "liked_issues": {
                "count": liked_issues.count(),
                "issues": liked_issues_serializer.data,
            },
            "commented_issues": {
                "count": total_comments_made,
                "issues": commented_issues_data,
            },
            "stats": {
                "total_issues_reported": user.reported_issues.count(),
                "total_resolved": user.reported_issues.filter(is_resolved=True).count(),
                "total_issues_liked": liked_issues.count(),
                "total_comments_made": total_comments_made,
                "total_images_added": user.reported_issues.aggregate(
                    total=Count("images")
                )["total"] or 0,
                "impact_rank": f"#{impact_rank}",
                "resolution_overview": resolution_overview,
                "category_breakdown": category_breakdown,
            },
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ProfileEditView(APIView):
    """
    Edit the profile information of the authenticated user.

    **Request Format (multipart/form-data):**
    - first_name: string (optional)
    - last_name: string (optional)
    - phone_number: string (optional)
    - profile_pic: file (optional)

    **Response:** Updated user object
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user

        # Update user fields if provided
        if "first_name" in request.data:
            user.first_name = request.data["first_name"]

        if "last_name" in request.data:
            user.last_name = request.data["last_name"]

        if "phone_number" in request.data:
            user.phone_number = request.data["phone_number"]

        if "profile_pic" in request.FILES:
            user.profile_pic = request.FILES["profile_pic"]

        user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExploreFeedView(APIView):
    """
    Get a paginated list of issues reported by other users for exploration.
    It will not include issues reported by the requesting user.

    **Request Parameters:**
    - page: integer (optional, default=1)
    - page_size: integer (optional, default=10)
    - search: string (optional) - search in title, description, address
    - category: string (optional) - filter by category
    - start_date: YYYY-MM-DD (optional) - filter issues created after this date
    - end_date: YYYY-MM-DD (optional) - filter issues created before this date
    - ordering: string (optional) - order by field (e.g., '-created_at', 'created_at')

    **Response:** Paginated list of issues with basic information
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Q
        from django.utils.dateparse import parse_date
        
        user = request.user

        # Get pagination parameters
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        # Validate pagination parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10

        # Get issues excluding those reported by the user
        issues = (
            Issue.objects.exclude(reported_by=user)
            .filter(is_archived=False)
        )

        # Apply search filter
        search = request.query_params.get("search", "").strip()
        if search:
            issues = issues.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(address__icontains=search) |
                Q(city__icontains=search)
            )

        # Apply category filter
        category = request.query_params.get("category", "").strip()
        if category:
            issues = issues.filter(category__iexact=category)

        # Apply date range filters
        start_date = request.query_params.get("start_date")
        if start_date:
            parsed_start = parse_date(start_date)
            if parsed_start:
                issues = issues.filter(created_at__date__gte=parsed_start)

        end_date = request.query_params.get("end_date")
        if end_date:
            parsed_end = parse_date(end_date)
            if parsed_end:
                issues = issues.filter(created_at__date__lte=parsed_end)

        # Apply ordering
        ordering = request.query_params.get("ordering", "-created_at")
        issues = issues.order_by(ordering)

        # Calculate pagination
        total_count = issues.count()
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        # Get paginated issues
        paginated_issues = issues[start_index:end_index]
        serializer = IssueListSerializer(paginated_issues, many=True)

        response_data = {
            "count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size,
            "results": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class AnalyticsView(APIView):
    """
    Get global analytics data for the Townspark ecosystem.

    Provides comprehensive statistics about all issues reporting patterns
    including resolution times, engagement metrics, and time-based trends.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all issues in the app
        all_issues = Issue.objects.all()

        # Basic counts
        total_issues_reported = all_issues.count()
        total_issues_resolved = all_issues.filter(is_resolved=True).count()

        # Engagement metrics on all issues
        total_likes_received = IssueLike.objects.count()
        total_comments_received = IssueComment.objects.count()

        # Resolution time statistics for resolved issues
        resolved_issues = all_issues.filter(is_resolved=True)

        # Calculate resolution times
        resolution_data = resolved_issues.annotate(
            resolution_time=ExpressionWrapper(
                F("resolved_at") - F("created_at"), output_field=DurationField()
            )
        )

        # Count issues by resolution time brackets
        now = timezone.now()
        solved_within_7_days = resolved_issues.filter(
            resolved_at__lte=F("created_at") + timedelta(days=7)
        ).count()

        solved_within_30_days = resolved_issues.filter(
            resolved_at__lte=F("created_at") + timedelta(days=30)
        ).count()

        # Average resolution time in days
        avg_resolution_time = None
        if resolution_data.exists():
            avg_seconds = resolution_data.aggregate(avg_time=Avg("resolution_time"))[
                "avg_time"
            ]
            if avg_seconds:
                avg_resolution_time = (
                    avg_seconds.total_seconds() / 86400
                )  # Convert to days

        # Issues reported over time (last 12 months)
        twelve_months_ago = now - timedelta(days=365)
        monthly_issues = []

        for i in range(12):
            month_start = twelve_months_ago + timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            count = all_issues.filter(
                created_at__gte=month_start, created_at__lt=month_end
            ).count()
            monthly_issues.append(
                {"month": month_start.strftime("%Y-%m"), "count": count}
            )

        # Category distribution
        category_stats = (
            all_issues.values("category")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Status breakdown
        status_breakdown = {
            "resolved": total_issues_resolved,
            "pending": all_issues.filter(is_resolved=False, is_archived=False).count(),
            "archived": all_issues.filter(is_archived=True).count(),
        }

        # Engagement rate (average likes + comments per issue)
        avg_likes_per_issue = (
            all_issues.annotate(_like_count=Count("likes")).aggregate(
                avg=Avg("_like_count")
            )["avg"]
            or 0
        )

        avg_comments_per_issue = (
            all_issues.annotate(_comment_count=Count("comments")).aggregate(
                avg=Avg("_comment_count")
            )["avg"]
            or 0
        )

        # Most engaged issue
        most_engaged_issue = (
            all_issues.annotate(engagement=Count("likes") + Count("comments"))
            .order_by("-engagement")
            .first()
        )

        most_engaged_issue_data = None
        if most_engaged_issue:
            most_engaged_issue_data = {
                "id": most_engaged_issue.id,
                "title": most_engaged_issue.title,
                "total_engagement": most_engaged_issue.likes.count()
                + most_engaged_issue.comments.count(),
            }

        # Recent activity (last 30 days)
        last_30_days = now - timedelta(days=30)
        recent_issues_count = all_issues.filter(created_at__gte=last_30_days).count()
        recent_activity_rate = (
            (recent_issues_count / 30) if recent_issues_count > 0 else 0
        )

        response_data = {
            "total_issues_reported": total_issues_reported,
            "total_issues_resolved": total_issues_resolved,
            "total_likes_received": total_likes_received,
            "total_comments_received": total_comments_received,
            "issues_reported_over_time": monthly_issues,
            "resolution_stats": {
                "solved_within_7_days": solved_within_7_days,
                "solved_within_30_days": solved_within_30_days,
                "average_resolution_time_days": round(avg_resolution_time, 2)
                if avg_resolution_time
                else None,
                "resolution_rate_percentage": round(
                    (total_issues_resolved / total_issues_reported * 100), 2
                )
                if total_issues_reported > 0
                else 0,
            },
            "status_breakdown": status_breakdown,
            "category_distribution": list(category_stats),
            "engagement_metrics": {
                "avg_likes_per_issue": round(avg_likes_per_issue, 2),
                "avg_comments_per_issue": round(avg_comments_per_issue, 2),
                "most_engaged_issue": most_engaged_issue_data,
            },
            "recent_activity": {
                "issues_last_30_days": recent_issues_count,
                "avg_issues_per_day": round(recent_activity_rate, 2),
            },
        }

        return Response(response_data, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    Retrieve the public profile information of another user.

    **Response:** User info, reported issues, and recent Activity (comments/reports)
    """
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Basic User Info (Public)
        user_info = {
            "id": target_user.id,
            "first_name": target_user.first_name,
            "last_name": target_user.last_name,
            "profile_pic": request.build_absolute_uri(target_user.profile_pic.url) if target_user.profile_pic else None,
            "date_joined": target_user.created_at,
            "email": target_user.email, # Maybe hide email? Or mask? User request says public details.
        }

        # Reported Issues (Public - not archived)
        all_reported = Issue.objects.filter(reported_by=target_user, is_archived=False).order_by("-created_at")
        reported_issues_serializer = IssueListSerializer(all_reported, many=True, context={'request': request})

        # Recent Comments
        recent_comments = IssueComment.objects.filter(commented_by=target_user).select_related('issue').order_by("-created_at")[:10]
        recent_comments_data = []
        for comment in recent_comments:
            recent_comments_data.append({
                "id": comment.id,
                "text": comment.text,
                "created_at": comment.created_at,
                "issue_id": comment.issue.id,
                "issue_title": comment.issue.title,
            })

        # Calculate stats
        impact_rank = User.objects.annotate(
            issue_count=Count('reported_issues')
        ).filter(issue_count__gt=target_user.reported_issues.count()).count() + 1
        
        stats = {
            "total_issues_reported": all_reported.count(),
            "total_resolved": all_reported.filter(is_resolved=True).count(),
            "total_comments_made": IssueComment.objects.filter(commented_by=target_user).count(),
            "impact_rank": f"#{impact_rank}",
        }

        response_data = {
            "user": user_info,
            "reported_issues": reported_issues_serializer.data,
            "recent_comments": recent_comments_data,
            "stats": stats,
        }

        return Response(response_data, status=status.HTTP_200_OK)
