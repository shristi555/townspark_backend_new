from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.
class PingView(APIView):
    permission_classes = [AllowAny]
    # authentication_classes = []

    def get(self, request, *args, **kwargs):
        return Response({}, status=200)

    def post(self, request, *args, **kwargs):
        return Response({}, status=200)
