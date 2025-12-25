
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Issue, IssueComment, IssueLike
from .permissions import IsOwnerOrStaff
from .serializers import IssueSerializer, IssueCommentSerializer
from django.shortcuts import get_object_or_404

from rest_framework.generics import UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAdminUser


"""
Creates new issues and images in a single API call.

"""


class IssueCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = IssueSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            issue = serializer.save()
            return Response(IssueSerializer(issue).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyIssuesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        issues = Issue.objects.filter(reported_by=request.user).prefetch_related(
            "images", "comments", "likes"
        )

        serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)


class IssueDetailView(APIView):
    def get(self, request, issue_id):
        issue = get_object_or_404(
            Issue.objects.prefetch_related("images", "comments", "likes"), id=issue_id
        )

        serializer = IssueSerializer(issue)
        return Response(serializer.data)


class IssueDetailView(APIView):
    def get(self, request, issue_id):
        issue = get_object_or_404(
            Issue.objects.prefetch_related("images", "comments", "likes"), id=issue_id
        )

        serializer = IssueSerializer(issue)
        return Response(serializer.data)


class IssueCommentsView(APIView):
    def get(self, request, id):
        comments = IssueComment.objects.filter(issue_id=id)
        serializer = IssueCommentSerializer(comments, many=True)
        return Response(serializer.data)


class CreateCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        issue_id = request.data.get("issue_id")
        text = request.data.get("text")

        if not issue_id or not text:
            return Response(
                {"detail": "issue_id and text are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comment = IssueComment.objects.create(
            issue_id=issue_id, text=text, commented_by=request.user
        )

        return Response(
            {"message": "Comment added successfully"}, status=status.HTTP_201_CREATED
        )


class LikeCreateView(APIView):
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
    def get(self, request, id):
        likes = IssueLike.objects.filter(issue_id=id)
        return Response(
            [{"user": like.liked_by.email, "time": like.created_at} for like in likes]
        )


class IssueUpdateView(UpdateAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsOwnerOrStaff]
    lookup_field = 'id'


class IssueDeleteView(DestroyAPIView):
    queryset = Issue.objects.all()
    permission_classes = [IsOwnerOrStaff]
    lookup_field = 'id'


class CommentDeleteView(DestroyAPIView):
    queryset = IssueComment.objects.all()
    permission_classes = [IsOwnerOrStaff]
    lookup_field = 'id'


class AdminIssueDeleteView(DestroyAPIView):
    queryset = Issue.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
