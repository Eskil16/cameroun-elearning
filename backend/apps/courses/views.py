import os
from rest_framework import generics, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings as django_settings
from django.utils import timezone

from .models import Category, Course, Module, Enrollment, Progress, CourseRating
from .serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    CourseCreateSerializer, ModuleSerializer, ModuleCreateSerializer,
    EnrollmentSerializer, ProgressSerializer, CourseRatingSerializer,
)
from apps.users.utils import api_response
from apps.social.models import FeedItem
from apps.reputation.services import grant_reputation


def get_lang(request):
    if hasattr(request, 'user') and request.user.is_authenticated:
        return request.user.preferred_language
    return 'fr'


class IsInstructorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ('instructor', 'admin', 'moderator')


class IsCourseOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.instructor == request.user or request.user.role in ('admin', 'moderator')


# ── Catégories ─────────────────────────────────────────────────────────────────

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


# ── Cours ──────────────────────────────────────────────────────────────────────

class CourseListView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'level', 'language', 'is_low_bandwidth']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'average_rating', 'enrollment_count']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Course.objects.filter(status='approved').select_related(
            'instructor', 'category'
        ).prefetch_related('modules')
        low_bw = self.request.query_params.get('low_bandwidth')
        if low_bw:
            qs = qs.filter(is_low_bandwidth=True)
        return qs


class CourseCreateView(generics.CreateAPIView):
    serializer_class = CourseCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructorOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        course = serializer.save(instructor=self.request.user, status='pending')
        FeedItem.objects.create(
            actor=self.request.user,
            item_type='course_published',
            content_fr=f'a soumis un nouveau cours : « {course.title} »',
            content_en=f'submitted a new course: "{course.title}"',
            course=course,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        lang = get_lang(request)
        return api_response(
            data=serializer.data,
            message_fr='Cours soumis pour validation. Un modérateur va examiner votre contenu.',
            message_en='Course submitted for review. A moderator will examine your content.',
            status_code=status.HTTP_201_CREATED,
            lang=lang,
        )


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCourseOwnerOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return CourseCreateSerializer
        return CourseDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role in ('moderator', 'admin'):
            return Course.objects.all()
        return Course.objects.filter(status='approved')


class MyCourseListView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(
            instructor=self.request.user
        ).select_related('category')


# ── Modules ────────────────────────────────────────────────────────────────────

class ModuleListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ModuleCreateSerializer
        return ModuleSerializer

    def get_queryset(self):
        return Module.objects.filter(course_id=self.kwargs['course_pk'])

    def perform_create(self, serializer):
        course = Course.objects.get(pk=self.kwargs['course_pk'])
        if course.instructor != self.request.user and self.request.user.role not in ('admin',):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied()
        module = serializer.save(course=course)

        # Calcul taille fichier
        size_mb = 0
        if module.video:
            size_mb += module.video.size / (1024 * 1024)
        if module.pdf:
            size_mb += module.pdf.size / (1024 * 1024)
        module.file_size_mb = round(size_mb, 2)
        module.save(update_fields=['file_size_mb'])
        course.update_size()


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Module.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ModuleCreateSerializer
        return ModuleSerializer


# ── Inscriptions ───────────────────────────────────────────────────────────────

class EnrollView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        lang = get_lang(request)
        try:
            course = Course.objects.get(pk=pk, status='approved')
        except Course.DoesNotExist:
            return api_response(
                message_fr='Cours introuvable.',
                message_en='Course not found.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
                lang=lang,
            )
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user, course=course
        )
        if created:
            course.enrollment_count += 1
            course.save(update_fields=['enrollment_count'])
        return api_response(
            data=EnrollmentSerializer(enrollment).data,
            message_fr='Inscription réussie.' if created else 'Déjà inscrit.',
            message_en='Enrolled successfully.' if created else 'Already enrolled.',
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            lang=lang,
        )


class MyEnrollmentsView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        enrolled_ids = Enrollment.objects.filter(
            user=self.request.user
        ).values_list('course_id', flat=True)
        return Course.objects.filter(id__in=enrolled_ids, status='approved')


# ── Progression ────────────────────────────────────────────────────────────────

class UpdateProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, module_pk):
        lang = get_lang(request)
        try:
            module = Module.objects.get(pk=module_pk)
        except Module.DoesNotExist:
            return api_response(
                message_fr='Module introuvable.',
                message_en='Module not found.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
                lang=lang,
            )

        percentage = float(request.data.get('percentage', 0))
        last_pos = int(request.data.get('last_position_seconds', 0))
        percentage = max(0, min(100, percentage))

        progress, _ = Progress.objects.update_or_create(
            user=request.user,
            module=module,
            defaults={
                'percentage': percentage,
                'last_position_seconds': last_pos,
                'completed': percentage >= 100,
            }
        )
        return api_response(
            data=ProgressSerializer(progress).data,
            message_fr='Progression sauvegardée.',
            message_en='Progress saved.',
            lang=lang,
        )


# ── Notes / Évaluations ────────────────────────────────────────────────────────

class CourseRatingView(generics.ListCreateAPIView):
    serializer_class = CourseRatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return CourseRating.objects.filter(
            course_id=self.kwargs['pk']
        ).select_related('user')

    def perform_create(self, serializer):
        course = Course.objects.get(pk=self.kwargs['pk'])
        from django.db.models import Avg
        from apps.courses.models import Progress as P
        modules = course.modules.all()
        if modules.exists():
            avg_prog = P.objects.filter(
                user=self.request.user, module__course=course
            ).aggregate(avg=Avg('percentage'))['avg'] or 0
            if avg_prog < 80:
                from rest_framework.exceptions import ValidationError
                raise ValidationError(
                    'Vous devez compléter 80% du cours avant de le noter. / '
                    'You must complete 80% of the course before rating it.'
                )
        rating = serializer.save(user=self.request.user, course=course)
        course.update_rating()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        lang = get_lang(request)
        return api_response(
            data=serializer.data,
            message_fr='Évaluation enregistrée. Merci !',
            message_en='Rating recorded. Thank you!',
            status_code=status.HTTP_201_CREATED,
            lang=lang,
        )
