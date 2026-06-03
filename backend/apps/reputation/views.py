from rest_framework import generics, permissions
from django.contrib.auth import get_user_model

from .models import Badge, UserBadge, ReputationEvent
from .serializers import (
    BadgeSerializer, UserBadgeSerializer,
    ReputationEventSerializer, LeaderboardSerializer,
)
from apps.users.utils import api_response

User = get_user_model()


class BadgeListView(generics.ListAPIView):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.AllowAny]


class LeaderboardView(generics.ListAPIView):
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return User.objects.filter(
            is_active=True
        ).order_by('-reputation_score')[:50]


class MyReputationEventsView(generics.ListAPIView):
    serializer_class = ReputationEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReputationEvent.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        return api_response(
            data={
                'total_score': request.user.reputation_score,
                'trust_display': request.user.trust_score_display,
                'events': serializer.data,
            },
            message_fr='Historique de réputation',
            message_en='Reputation history',
            lang=request.user.preferred_language,
        )
