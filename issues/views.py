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
    - category: string (required)
    - address: string (optional)
    - uploaded_images: file[] (required,minimum of 1 max of 10, at least 1-10 images)

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

    **Response:** List of issue objects with images and counts
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        issues = Issue.objects.filter(reported_by=request.user).prefetch_related(
            "images", "comments", "likes"
        )

        serializer = IssueListSerializer(issues, many=True)
        return Response(serializer.data)


class IssueDetailView(APIView):
    """
    Get detailed information about a specific issue.

    **URL Parameter:** issue_id (integer)

    **Response:** Detailed issue object with images, comments, and likes
    """

    def get(self, request, issue_id):
        issue = get_object_or_404(
            Issue.objects.prefetch_related("images", "comments", "likes"), id=issue_id
        )

        serializer = IssueDetailSerializer(issue)
        return Response(serializer.data)


class IssueCommentsView(APIView):
    """
    Get all comments for a specific issue.

    **URL Parameter:** id (integer)

    **Response:** List of comment objects
    """

    def get(self, request, id):
        comments = IssueComment.objects.filter(issue_id=id)
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
            # print(f"Recieved request data: {request.data}")
            return Response(
                {"detail": "issue_id is mandatory but not given"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not text:
            return Response(
                {"detail": "comment text is mandatory but not given"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comment = IssueComment.objects.create(
            issue_id=issue_id, text=text, commented_by=request.user
        )

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

        like, created = IssueLike.objects.get_or_create(
            issue_id=issue_id, liked_by=request.user
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

        like = IssueLike.objects.filter(issue_id=issue_id, liked_by=request.user)

        if like.exists():
            like.delete()
            return Response({"liked": False})

        IssueLike.objects.create(issue_id=issue_id, liked_by=request.user)

        return Response({"liked": True})


class IssueLikesView(APIView):
    """
    Get all likes for a specific issue.

    **URL Parameter:** id (integer)

    **Response:** List of objects with user email and timestamp
    """

    def get(self, request, id):
        likes = IssueLike.objects.filter(issue_id=id)
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
        "category": string (optional),
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
