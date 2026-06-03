from django.urls import path
from .views import BadgeListView, LeaderboardView, MyReputationEventsView

urlpatterns = [
    path('badges/', BadgeListView.as_view(), name='badge-list'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('my-history/', MyReputationEventsView.as_view(), name='reputation-history'),
]
