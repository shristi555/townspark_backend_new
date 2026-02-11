from django.urls import path
from .views import UniversalSearchView, SuggestionView

urlpatterns = [
    path('search/', UniversalSearchView.as_view(), name='universal-search'),
    path('suggestions/', SuggestionView.as_view(), name='search-suggestions'),
]
