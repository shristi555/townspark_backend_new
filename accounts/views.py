from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.serializers import CustomTokenObtainPairSerializer
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView

from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
class CustomTokenObtainView(TokenObtainPairView):
    """
     Custom view to handle user login with additional checks:
    - Verify if the email exists.
    - Check if the account is active.
    - Validate the password.

    it is intended to give a detailed error response for each failure case. overriding the default behavior of djoser's TokenCreateView.
    """

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
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
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        
        if refresh_token:
            request.data['refresh'] = refresh_token
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Set new access token cookie
            access_token = response.data.get('access')
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=access_token,
                expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            )
            
            # Set new refresh token cookie if rotation is enabled
            if 'refresh' in response.data:
                refresh_token = response.data.get('refresh')
                response.set_cookie(
                    key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                    value=refresh_token,
                    expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                )
        
        return response


class CustomTokenVerifyView(TokenVerifyView):
    """
    Verifies token from cookie if not in request body.
    """
    def post(self, request, *args, **kwargs):
        # Try to get token from cookie if not in body
        if 'token' not in request.data:
            token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
            if token:
                request.data['token'] = token
        
        return super().post(request, *args, **kwargs)



class LogoutView(APIView):
    """
    Clears authentication cookies on logout.
    """
    def post(self, request):
        response = Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK
        )
        
        # Delete access token cookie
        response.delete_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )
        
        # Delete refresh token cookie
        response.delete_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
            path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )
        
        return response

