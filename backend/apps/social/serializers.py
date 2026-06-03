from rest_framework import serializers
from .models import Follow, FeedItem, Like
from apps.users.serializers import UserPublicSerializer
from apps.courses.serializers import CourseListSerializer


class FollowSerializer(serializers.ModelSerializer):
    following = UserPublicSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'following', 'created_at']


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'feed_item', 'created_at']


class FeedItemSerializer(serializers.ModelSerializer):
    actor = UserPublicSerializer(read_only=True)
    course = CourseListSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = FeedItem
        fields = [
            'id', 'actor', 'item_type', 'content_fr', 'content_en',
            'course', 'likes_count', 'is_liked', 'created_at',
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
