from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Issue, IssueComment, IssueLike
from .permissions import IsOwnerOrStaff
from .serializers import (
    IssueCreateSerializer,
    IssueListSerializer,
    IssueDetailSerializer,
    IssueUpdateSerializer,
    IssueCommentSerializer,
)
from django.shortcuts import get_object_or_404

from rest_framework.generics import UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAdminUser


class IssueCreateView(APIView):
    """
    Create a new issue with images.

    **Request Format (multipart/form-data):**
    - title: string (required)
    - description: string (required)
    - category_id: integer (optional) OR category_name: string (optional) - one is required
    - address: string (optional)
    - uploaded_images: file[] (required, minimum of 1 max of 10)

    **Response:** Created issue object with status 201
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = IssueCreateSerializer(
            data=request.data, context={"request": request}
        )
        try:
            if serializer.is_valid():
                issue = serializer.save()
                return Response(
                    IssueDetailSerializer(issue).data, status=status.HTTP_201_CREATED
                )
        except Exception as e:
            # Log the actual error
            print(f"Error creating issue: {str(e)}")
            import traceback

            traceback.print_exc()
            return Response(
                {"detail": f"Error creating issue: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyIssuesView(APIView):
    """
    Get all issues reported by the authenticated user.

    **Response:** List of issue objects with images, counts, and progress updates
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        issues = (
            Issue.objects.filter(reported_by=request.user)
            .select_related("reported_by")
            .prefetch_related(
                "images",
                "comments",
                "likes",
                "progress_updates",
                "progress_updates__updated_by",
                "progress_updates__images",  # NEW - optimize progress images
            )
        )

        serializer = IssueListSerializer(issues, many=True)

        return Response(serializer.data)


class IssueDetailView(APIView):
    """
    Get detailed information about a specific issue.

    **URL Parameter:** issue_id (integer)

    **Response:** Detailed issue object with images, comments, likes, and progress updates
    """

    def get(self, request, issue_id):
        issue = get_object_or_404(
            Issue.objects.select_related("reported_by").prefetch_related(
                "images",
                "comments",
                "comments__commented_by",
                "likes",
                "progress_updates",
                "progress_updates__updated_by",
                "progress_updates__images",  # NEW - optimize progress images
            ),
            id=issue_id,
        )

        serializer = IssueDetailSerializer(issue)
        data = serializer.data
        data["requesting_user_id"] = (
            request.user.id if request.user.is_authenticated else None
        )
        return Response(data)


class IssueCommentsView(APIView):
    """
    Get all comments for a specific issue.

    **URL Parameter:** id (integer)

    **Response:** List of comment objects
    """

    def get(self, request, id):
        comments = IssueComment.objects.filter(issue_id=id).select_related(
            "commented_by"
        )
        serializer = IssueCommentSerializer(comments, many=True)
        return Response(serializer.data)


class CreateCommentView(APIView):
    """
    Add a comment to an issue.

    **Request Format (JSON):**
    {
        "issue_id": integer (required),
        "text": string (required)
    }

    **Response:** Success message with status 201
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        issue_id = request.data.get("issue_id")
        text = request.data.get("text")

        if not issue_id and not text:
            return Response(
                {
                    "detail": "issue_id and comment text are mandatory but none of them are given"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not issue_id:
            return Response(
                {"detail": "issue_id is mandatory but not given"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not text:
            return Response(
                {"detail": "comment text is mandatory but not given"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate issue exists
        issue = get_object_or_404(Issue, id=issue_id)

        IssueComment.objects.create(issue=issue, text=text, commented_by=request.user)

        return Response(
            {"message": "Comment added successfully"}, status=status.HTTP_201_CREATED
        )


class LikeCreateView(APIView):
    """
    Like an issue (one-time only).

    **Request Format (JSON):**
    {
        "issue_id": integer (required)
    }

    **Response:** Success message or error if already liked
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        issue_id = request.data.get("issue_id")

        if not issue_id:
            return Response({"detail": "issue_id required"}, status=400)

        # Validate issue exists
        issue = get_object_or_404(Issue, id=issue_id)

        like, created = IssueLike.objects.get_or_create(
            issue=issue, liked_by=request.user
        )

        if not created:
            return Response({"detail": "Already liked"}, status=400)

        return Response({"message": "Liked"}, status=201)


class ToggleLikeView(APIView):
    """
    Toggle like status on an issue.

    **Request Format (JSON):**
    {
        "issue_id": integer (required)
    }

    **Response:**
    {
        "liked": boolean (true if liked, false if unliked)
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        issue_id = request.data.get("issue_id")

        if not issue_id:
            return Response({"detail": "issue_id required"}, status=400)

        # Validate issue exists
        issue = get_object_or_404(Issue, id=issue_id)

        like = IssueLike.objects.filter(issue=issue, liked_by=request.user)

        if like.exists():
            like.delete()
            return Response({"liked": False})

        IssueLike.objects.create(issue=issue, liked_by=request.user)

        return Response({"liked": True})


class IssueLikesView(APIView):
    """
    Get all likes for a specific issue.

    **URL Parameter:** id (integer)

    **Response:** List of objects with user email and timestamp
    """

    def get(self, request, id):
        likes = IssueLike.objects.filter(issue_id=id).select_related("liked_by")
        return Response(
            [{"user": like.liked_by.email, "time": like.created_at} for like in likes]
        )


class IssueUpdateView(UpdateAPIView):
    """
    Update an existing issue.

    **URL Parameter:** id (integer)

    **Request Format (JSON):**
    {
        "title": string (optional),
        "description": string (optional),
        "category_id": integer (optional) OR category_name: string (optional),
        "address": string (optional),
        "is_resolved": boolean (optional)
    }

    **Response:** Updated issue object
    """

    queryset = Issue.objects.all()
    serializer_class = IssueUpdateSerializer
    permission_classes = [IsOwnerOrStaff]
    lookup_field = "id"


class IssueDeleteView(DestroyAPIView):
    """
    Delete an issue (owner or staff only).

    **URL Parameter:** id (integer)

    **Response:** 204 No Content on success
    """

    queryset = Issue.objects.all()
    permission_classes = [IsOwnerOrStaff]
    lookup_field = "id"


class CommentDeleteView(DestroyAPIView):
    """
    Delete a comment (owner or staff only).

    **URL Parameter:** id (integer)

    **Response:** 204 No Content on success
    """

    queryset = IssueComment.objects.all()
    permission_classes = [IsOwnerOrStaff]
    lookup_field = "id"


class AdminIssueDeleteView(DestroyAPIView):
    """
    Delete any issue (admin only).

    **URL Parameter:** id (integer)

    **Response:** 204 No Content on success
    """

    queryset = Issue.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = "id"


class ArchiveIssueView(APIView):
    """
    Archive an issue.
    Only admin or issue creator can archive.

    **Request Format (URL Parameter):**
    /archive/<int:issue_id>/

    **Response:** Success message with issue_id
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, issue_id):
        if not issue_id:
            return Response(
                {"error": "issue_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        issue = get_object_or_404(Issue, id=issue_id)

        # Check if user is admin or the one who reported the issue
        if not (request.user.is_staff or issue.reported_by == request.user):
            return Response(
                {"error": "You don't have permission to archive this issue"},
                status=status.HTTP_403_FORBIDDEN,
            )

        issue.is_archived = True
        issue.save()
        return Response(
            {"message": "Issue archived successfully", "issue_id": issue.id},
            status=status.HTTP_200_OK,
        )


class UnarchiveIssueView(APIView):
    """
    Unarchive an issue.
    Only admin or issue creator can unarchive.

    **Request Format (URL Parameter):**
    /unarchive/<int:issue_id>/

    **Response:** Success message with issue_id
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, issue_id):
        if not issue_id:
            return Response(
                {"error": "issue_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        issue = get_object_or_404(Issue, id=issue_id)

        # Check if user is admin or the one who reported the issue
        if not (request.user.is_staff or issue.reported_by == request.user):
            return Response(
                {"error": "You don't have permission to unarchive this issue"},
                status=status.HTTP_403_FORBIDDEN,
            )

        issue.is_archived = False
        issue.save()
        return Response(
            {"message": "Issue unarchived successfully", "issue_id": issue.id},
            status=status.HTTP_200_OK,
        )


