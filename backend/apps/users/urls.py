from django.urls import path
from .views import UserMeView, UserPublicProfileView
from apps.social.views import FollowView, UnfollowView, FollowersListView, FollowingListView

urlpatterns = [
    path('me/', UserMeView.as_view(), name='user-me'),
    path('<int:pk>/', UserPublicProfileView.as_view(), name='user-profile'),
    path('<int:pk>/follow/', FollowView.as_view(), name='user-follow'),
    path('<int:pk>/unfollow/', UnfollowView.as_view(), name='user-unfollow'),
    path('<int:pk>/followers/', FollowersListView.as_view(), name='user-followers'),
    path('<int:pk>/following/', FollowingListView.as_view(), name='user-following'),
]
