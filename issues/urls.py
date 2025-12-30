# python
from django.urls import path
from .views import *
from .progress import views as progress_views

comment_patterns = [
    path("comments/create/", CreateCommentView.as_view(), name="create-comment"),
    path("comments/of/<int:id>/", IssueCommentsView.as_view(), name="issue-comments"),
    path(
        "comments/delete/<int:id>/", CommentDeleteView.as_view(), name="delete-comment"
    ),
]

like_patterns = [
    path("likes/create/", LikeCreateView.as_view(), name="create-like"),
    path("likes/toggle/", ToggleLikeView.as_view(), name="toggle-like"),
    path("likes/of/<int:id>/", IssueLikesView.as_view(), name="issue-likes"),
]

progress_patterns = [
    path(
        "progress/create/",
        progress_views.CreateIssueProgressView.as_view(),
        name="create-issue-progress",
    ),
    path(
        "progress/list/<int:issue_id>/",
        progress_views.ListIssueProgressView.as_view(),
        name="list-issue-progress",
    ),
    path(
        "progress/<int:progress_id>/",
        progress_views.GetIssueProgressView.as_view(),
        name="get-issue-progress",
    ),
    path(
        "progress/delete/<int:progress_id>/",
        progress_views.DeleteIssueProgressView.as_view(),
        name="delete-issue-progress",
    ),
]

urlpatterns = [
    path("create/", IssueCreateView.as_view()),
    path("mine/", MyIssuesView.as_view()),
    path("of/<int:issue_id>/", IssueDetailView.as_view()),
    path("archive/<int:issue_id>/", ArchiveIssueView.as_view(), name="archive-issue"),
    path(
        "unarchive/<int:issue_id>/",
        UnarchiveIssueView.as_view(),
        name="unarchive-issue",
    ),
    path("update/<int:id>/", IssueUpdateView.as_view()),
    path("delete/<int:id>/", IssueDeleteView.as_view()),
  ]

# correct way to add extra patterns
urlpatterns += progress_patterns + comment_patterns + like_patterns
