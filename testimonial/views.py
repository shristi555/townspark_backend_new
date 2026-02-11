from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Avg, F
from .models import Testimonial
from .serializers import TestimonialSerializer
from accounts.models import User
from issues.models import Issue

class LandingPageDataView(APIView):
    """
    API View to provide global stats and testimonials for the landing page.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # 1. Calculate Stats
        total_users = User.objects.filter(is_active=True).count()
        issues_resolved = Issue.objects.filter(is_resolved=True).count()
        cities_connected = Issue.objects.exclude(city__isnull=True).exclude(city="").values("city").distinct().count()
        
        # Calculate Avg Response Time (in hours) safely
        avg_response_hours = 48.0 # Default fallback
        try:
            avg_response_data = Issue.objects.filter(
                is_resolved=True, 
                resolved_at__isnull=False
            ).annotate(
                duration=F('resolved_at') - F('created_at')
            ).aggregate(
                avg_duration=Avg('duration')
            )
            
            if avg_response_data['avg_duration']:
                avg_response_hours = round(avg_response_data['avg_duration'].total_seconds() / 3600, 1)
        except Exception as e:
            print(f"Stats calculation error: {e}")
            pass

        # 2. Get Testimonials (limit to 6)
        testimonials = Testimonial.objects.filter(is_displayed=True).order_by('-rating', '-created_at')[:6]
        testimonial_serializer = TestimonialSerializer(testimonials, many=True)

        data = {
            "stats": {
                "total_users": total_users,
                "issues_resolved": issues_resolved,
                "cities_connected": cities_connected,
                "avg_response_time_hrs": avg_response_hours
            },
            "testimonials": testimonial_serializer.data
        }

        return Response(data, status=status.HTTP_200_OK)

class RatePlatformView(APIView):
    """
    Handles retrieval, creation, and updating of the user's platform rating.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Retrieve the current user's rating if it exists."""
        try:
            testimonial = Testimonial.objects.get(user=request.user)
            serializer = TestimonialSerializer(testimonial)
            return Response(serializer.data)
        except Testimonial.DoesNotExist:
            return Response({"detail": "No rating found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Create a new rating for the platform."""
        if Testimonial.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "You have already rated the platform. Use PATCH to update."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = TestimonialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """Update an existing rating."""
        try:
            testimonial = Testimonial.objects.get(user=request.user)
        except Testimonial.DoesNotExist:
            return Response({"detail": "No rating found to update"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TestimonialSerializer(testimonial, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
