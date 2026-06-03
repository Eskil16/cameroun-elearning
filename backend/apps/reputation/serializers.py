from rest_framework import serializers
from .models import Badge, UserBadge, ReputationEvent
from apps.users.serializers import UserPublicSerializer


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = [
            'id', 'slug', 'name_fr', 'name_en',
            'description_fr', 'description_en',
            'icon', 'required_score', 'is_special',
        ]


class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = UserBadge
        fields = ['id', 'user', 'badge', 'earned_at']


class ReputationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReputationEvent
        fields = [
            'id', 'event_type', 'points',
            'description_fr', 'description_en', 'created_at',
        ]


class LeaderboardSerializer(serializers.ModelSerializer):
    badges_count = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        from django.contrib.auth import get_user_model
        model = get_user_model()
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'reputation_score', 'trust_score_display',
            'role', 'avatar_url', 'badges_count',
        ]

    def get_badges_count(self, obj):
        return obj.badges.count()

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None
