from django.urls import path
from djoser.views import UserViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from accounts.views import CustomTokenObtainView
from accounts.helpers.update_profile_pic import (
    UpdateProfilePictureView,
    ProfilePictureSerializer,
)

urlpatterns = [
    # Auth
    path("register/", UserViewSet.as_view({"post": "create"}), name="register"),
    path("login/", CustomTokenObtainView.as_view(), name="login"),
    # Token management
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # User info
    path(
        "me/", UserViewSet.as_view({"get": "me", "put": "me", "patch": "me"}), name="me"
    ),
    path(
        "me/update/profile_pic/",
        UpdateProfilePictureView.as_view(),
        name="update_profile_pic",
    ),
]
