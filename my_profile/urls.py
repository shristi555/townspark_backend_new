from my_profile.views import (
    GetProfileInfoView,
    ProfileEditView,
    ExploreFeedView,
    AnalyticsView,
    UserProfileView,
)
from django.urls import path


urlpatterns = [
    path("", GetProfileInfoView.as_view(), name="get-profile-info"),
    path("update/", ProfileEditView.as_view(), name="update-profile-info"),
    path("edit/", ProfileEditView.as_view(), name="edit-profile-info"),
    path("explore/", ExploreFeedView.as_view(), name="explore-profiles"),
    path("analytics/", AnalyticsView.as_view(), name="profile-analytics"),
    path("user/<int:user_id>/", UserProfileView.as_view(), name="user-profile"),
]
