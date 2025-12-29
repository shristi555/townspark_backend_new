from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from issues.models import Issue, IssueProgress
from issues.serializers import IssueProgressSerializer


class CreateIssueProgressView(APIView):
    """
    Create a new progress update for an issue.
    Only admin or issue creator can add progress updates.

    **Request Format (JSON):**
    {
        "issue_id": integer (required),
        "title": string (required),
        "description": string (required)
    }

    **Response:** List of all progress updates for the issue with status 201
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        issue_id = request.data.get("issue_id")

        if not issue_id:
            return Response(
                {"error": "issue_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        issue = get_object_or_404(Issue, id=issue_id)

        # Check if user is admin or issue creator
        if not (request.user.is_staff or issue.reported_by == request.user):
            return Response(
                {
                    "error": "You don't have permission to update progress on this issue. Try commenting instead."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = IssueProgressSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            # Get all progress updates for the issue after creating the new one
            all_progress = IssueProgress.objects.filter(issue=issue).order_by(
                "-created_at"
            )
            progress_serializer = IssueProgressSerializer(all_progress, many=True)

            return Response(progress_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListIssueProgressView(APIView):
    """
    List all progress updates for a specific issue.

    **URL Parameter:** issue_id (integer)

    **Response:** List of progress update objects
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, issue_id):
        issue = get_object_or_404(Issue, id=issue_id)
        progress_updates = IssueProgress.objects.filter(issue=issue).order_by(
            "-created_at"
        )
        serializer = IssueProgressSerializer(progress_updates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetIssueProgressView(APIView):
    """
    Get a specific progress update.

    **URL Parameter:** progress_id (integer)

    **Response:** Progress update object
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, progress_id):
        progress = get_object_or_404(IssueProgress, id=progress_id)
        serializer = IssueProgressSerializer(progress)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteIssueProgressView(APIView):
    """
    Delete a progress update.
    Only admin or the user who created the progress can delete it.

    **URL Parameter:** progress_id (integer)

    **Response:** Success message with status 204
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, progress_id):
        progress = get_object_or_404(IssueProgress, id=progress_id)

        # Check if user is admin or the one who created the progress
        if not (request.user.is_staff or progress.updated_by == request.user):
            return Response(
                {"error": "You do not have permission to delete this progress update"},
                status=status.HTTP_403_FORBIDDEN,
            )

        progress.delete()
        return Response(
            {"message": "Progress update deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
