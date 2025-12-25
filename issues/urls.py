from django.urls import path
from .views import *

urlpatterns = [
    path("create/", IssueCreateView.as_view()),
    path("mine/", MyIssuesView.as_view()),
    path("of/<int:issue_id>/", IssueDetailView.as_view()),
    path("comments/of/<int:id>/", IssueCommentsView.as_view()),
    path("comments/create/", CreateCommentView.as_view()),
    path("likes/create/", LikeCreateView.as_view()),
    path("likes/toggle/", ToggleLikeView.as_view()),
    path("likes/of/<int:id>/", IssueLikesView.as_view()),
    path("update/<int:id>/", IssueUpdateView.as_view()),
    path("delete/<int:id>/", IssueDeleteView.as_view()),
    path("comments/delete/<int:id>/", CommentDeleteView.as_view()),
]
