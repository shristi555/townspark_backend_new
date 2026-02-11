from django.urls import path
from .views import LandingPageDataView, RatePlatformView

urlpatterns = [
    path("landing-data/", LandingPageDataView.as_view(), name="landing-page-data"),
    path("rate/", RatePlatformView.as_view(), name="rate-platform"),
]
