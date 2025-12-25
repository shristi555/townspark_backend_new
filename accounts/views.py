from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts import serializers
from accounts.serializers import CustomTokenObtainPairSerializer


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
