from django.urls import path
from .views import FeedView, LikeToggleView

urlpatterns = [
    path('feed/', FeedView.as_view(), name='feed'),
    path('feed/<int:pk>/like/', LikeToggleView.as_view(), name='feed-like'),
]
