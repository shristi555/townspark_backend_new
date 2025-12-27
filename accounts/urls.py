from django.urls import path
from djoser.views import UserViewSet

from accounts.views import (
    CustomTokenObtainView,
    CustomTokenRefreshView,
    LogoutView,
    CustomTokenVerifyView,
    CustomSignupViewSet,
)
from accounts.update.views import (
    UpdateProfilePictureView,
)

urlpatterns = [
    # Auth
    path("register/", CustomSignupViewSet.as_view({"post": "create"}), name="register"),
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
    path("logout/", LogoutView.as_view(), name="logout"),
]
