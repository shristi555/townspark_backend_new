from django.urls import path
from djoser.views import UserViewSet

from accounts.views import (
    CustomTokenObtainView,
    CustomTokenRefreshView,
    LogoutView,
    CustomTokenVerifyView,
    DebugSignupView,
)
from accounts.update.views import UpdateProfilePictureView, ProfileUpdateView

urlpatterns = [
    # Auth
    path("register/", DebugSignupView.as_view(), name="register"),
    path("login/", CustomTokenObtainView.as_view(), name="login"),
    # Token management
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", CustomTokenVerifyView.as_view(), name="token_verify"),
    # User info
    path(
        "me/", UserViewSet.as_view({"get": "me", "put": "me", "patch": "me"}), name="me"
    ),
    path(
        "me/update/profile_pic/",
        UpdateProfilePictureView.as_view(),
        name="update_profile_pic",
    ),
    path(
        "me/update/",
        ProfileUpdateView.as_view(),
        name="update_profile",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),

    # path("firstname/update/", FirstNameUpdateView.as_view(), name="update-firstname"),
    # path("password/update/", PasswordUpdateView.as_view(), name="update-password"),

]
