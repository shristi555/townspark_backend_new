from django.urls import path
from .views import *

urlpatterns = [path("", PingView.as_view(), name="ping")]
