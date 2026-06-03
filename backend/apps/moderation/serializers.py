from rest_framework import serializers
from .models import Report, ModerationReview
from apps.users.serializers import UserPublicSerializer
from apps.courses.serializers import CourseListSerializer


class ReportSerializer(serializers.ModelSerializer):
    reporter = UserPublicSerializer(read_only=True)

    class Meta:
        model = Report
        fields = [
            'id', 'reporter', 'course', 'reason', 'details',
            'is_valid', 'reviewed_at', 'created_at',
        ]
        read_only_fields = ['reporter', 'is_valid', 'reviewed_at']


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['course', 'reason', 'details']


class ModerationReviewSerializer(serializers.ModelSerializer):
    moderator = UserPublicSerializer(read_only=True)
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = ModerationReview
        fields = ['id', 'moderator', 'course', 'decision', 'comment', 'created_at']
        read_only_fields = ['moderator']


class ModerationReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationReview
        fields = ['decision', 'comment']
