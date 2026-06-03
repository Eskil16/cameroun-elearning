from rest_framework import serializers
from .models import Category, Course, Module, Enrollment, Progress, CourseRating
from apps.users.serializers import UserPublicSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name_fr', 'name_en', 'slug', 'icon',
                  'description_fr', 'description_en']


class ModuleSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 'order',
            'video_url', 'pdf_url', 'duration_minutes',
            'file_size_mb', 'is_downloadable', 'user_progress',
        ]
        read_only_fields = ['file_size_mb']

    def get_video_url(self, obj):
        request = self.context.get('request')
        if obj.video_compressed and request:
            return request.build_absolute_uri(obj.video_compressed.url)
        if obj.video and request:
            return request.build_absolute_uri(obj.video.url)
        return None

    def get_pdf_url(self, obj):
        request = self.context.get('request')
        if obj.pdf and request:
            return request.build_absolute_uri(obj.pdf.url)
        return None

    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                p = obj.progress.get(user=request.user)
                return {'percentage': p.percentage, 'completed': p.completed,
                        'last_position': p.last_position_seconds}
            except Progress.DoesNotExist:
                pass
        return {'percentage': 0, 'completed': False, 'last_position': 0}


class ModuleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = [
            'title', 'description', 'order',
            'video', 'pdf', 'duration_minutes', 'is_downloadable',
        ]


class CourseListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    instructor = UserPublicSerializer(read_only=True)
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'category', 'instructor',
            'level', 'language', 'status', 'is_low_bandwidth',
            'total_size_mb', 'average_rating', 'rating_count',
            'enrollment_count', 'thumbnail_url', 'created_at',
        ]

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None


class CourseDetailSerializer(CourseListSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    user_overall_progress = serializers.SerializerMethodField()

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + [
            'modules', 'is_enrolled', 'user_overall_progress',
            'rejection_reason', 'report_count', 'updated_at',
        ]

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(user=request.user).exists()
        return False

    def get_user_overall_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            modules = obj.modules.all()
            if not modules:
                return 0
            total = sum(
                obj.progress.filter(user=request.user).first().percentage
                if hasattr(obj, 'progress') else 0
                for obj in modules
            )
            # simpler approach
            from apps.courses.models import Progress as P
            progresses = P.objects.filter(user=request.user, module__course=obj)
            if not progresses.exists():
                return 0
            return round(
                sum(p.percentage for p in progresses) / modules.count(), 1
            )
        return 0


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'title', 'description', 'category', 'level',
            'language', 'thumbnail',
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'enrolled_at', 'completed', 'completion_date']
        read_only_fields = ['enrolled_at', 'completion_date']


class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = ['module', 'percentage', 'last_position_seconds', 'completed']


class CourseRatingSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = CourseRating
        fields = ['id', 'user', 'stars', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']
