from djoser.views import UserViewSet
from accounts.serializers import CustomTokenObtainPairSerializer
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView

from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView

from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.permissions import AllowAny


class DebugSignupView(APIView):
    """
    Debug endpoint to see what's being received during signup.
    Remove this in production!
    """

    permission_classes = [AllowAny]

    def post(self, request):
        print("=" * 50)
        print("SIGNUP DEBUG INFO")
        print("=" * 50)
        print(f"Request Data: {request.data}")
        print(f"Content Type: {request.content_type}")
        print(f"Data Keys: {list(request.data.keys())}")

        from .serializers import UserCreateSerializer

        serializer = UserCreateSerializer(data=request.data)

        if not serializer.is_valid():
            print(f"Validation Errors: {serializer.errors}")
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = serializer.save()
            print(f"User created successfully: {user.email}")
            return Response(
                {
                    "message": "User created successfully",
                    "user": user.get_user_info(),
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            import traceback

            traceback.print_exc()
            return Response({"errors": e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Create your views here.
class CustomSignupViewSet(UserViewSet):
    """
    Custom signup viewset to handle user registration.

    it uses djoser's UserViewSet as a base.

    for now we will see if the user already is authenticated and prevent re-registration.
    """

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(
                {"detail": "User is already logged in. You need to logout first."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)


class CustomTokenObtainView(TokenObtainPairView):
    """
     Custom view to handle user login with additional checks:
    - Verify if the email exists.
    - Check if the account is active.
    - Validate the password.

    it is intended to give a detailed error response for each failure case. overriding the default behavior of djoser's TokenCreateView.
    """

    permission_classes = [AllowAny]

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # checks are handled in serializer
        if request.user.is_authenticated:
            return Response(
                {"detail": "User is already logged in. You need to logout first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            # extract tokens from response data
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")

            # Set Access Token Cookie
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                value=access_token,
                expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            )
            # Set Refresh Token Cookie
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
                value=refresh_token,
                expires=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            )

        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom refresh view that reads refresh token from cookie
    and returns new tokens as cookies.
    """

    def post(self, request, *args, **kwargs):
        # Try to get refresh token from cookie
        refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"], None
        )

        if refresh_token is None:
            refresh_token = request.data.get("refresh", None)

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if refresh_token:
            request.data["refresh"] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Set new access token cookie
            access_token = response.data.get("access")
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                value=access_token,
                expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            )

            # Set new refresh token cookie if rotation is enabled
            if "refresh" in response.data:
                refresh_token = response.data.get("refresh")
                response.set_cookie(
                    key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
                    value=refresh_token,
                    expires=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
                    secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                    httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                    samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                )

        return response


class CustomTokenVerifyView(TokenVerifyView):
    """
    Verifies token from cookie if not in request body.
    """

    def post(self, request, *args, **kwargs):
        # Try to get token from cookie if not in body
        if "token" not in request.data:
            access_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])

            if not access_token:
                return Response(
                    {"detail": "No access token provided."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Make request.data mutable and add token
            request._full_data = {"token": access_token}

        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """
    Clears authentication cookies on logout.
    """

    def post(self, request):
        response = Response(
            {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
        )

        # Delete access token cookie
        response.delete_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )

        # Delete refresh token cookie
        response.delete_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
            path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )

        return response
