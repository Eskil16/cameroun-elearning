from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.conf import settings as django_settings
from django.utils import timezone

from .models import Report, ModerationReview
from .serializers import (
    ReportSerializer, ReportCreateSerializer,
    ModerationReviewSerializer, ModerationReviewCreateSerializer,
)
from apps.courses.models import Course
from apps.users.utils import api_response
from apps.reputation.services import grant_reputation


def get_lang(request):
    if request.user.is_authenticated:
        return request.user.preferred_language
    return 'fr'


class CanModerate(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_moderate()


class ReportCourseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        lang = get_lang(request)
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return api_response(
                message_fr='Cours introuvable.',
                message_en='Course not found.',
                success=False, status_code=status.HTTP_404_NOT_FOUND, lang=lang,
            )

        if Report.objects.filter(reporter=request.user, course=course).exists():
            return api_response(
                message_fr='Vous avez déjà signalé ce cours.',
                message_en='You have already reported this course.',
                success=False, status_code=status.HTTP_400_BAD_REQUEST, lang=lang,
            )

        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(reporter=request.user, course=course)

        course.report_count += 1
        threshold = django_settings.REPORT_QUARANTINE_THRESHOLD
        if course.report_count >= threshold and course.status == 'approved':
            course.status = 'quarantine'
        course.save(update_fields=['report_count', 'status'])

        return api_response(
            message_fr='Signalement enregistré. Merci pour votre vigilance.',
            message_en='Report submitted. Thank you for your vigilance.',
            status_code=status.HTTP_201_CREATED, lang=lang,
        )


class ModerationQueueView(generics.ListAPIView):
    serializer_class = __import__(
        'apps.courses.serializers', fromlist=['CourseDetailSerializer']
    ).CourseDetailSerializer
    permission_classes = [CanModerate]

    def get_queryset(self):
        return Course.objects.filter(
            status__in=['pending', 'quarantine']
        ).select_related('instructor', 'category').order_by('created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        from apps.courses.serializers import CourseListSerializer
        serializer = CourseListSerializer(
            page or queryset, many=True, context={'request': request}
        )
        data = serializer.data
        return api_response(
            data={'results': data, 'count': queryset.count()},
            message_fr=f'{queryset.count()} cours en attente de modération.',
            message_en=f'{queryset.count()} courses pending moderation.',
            lang=get_lang(request),
        )


class ModerationReviewView(APIView):
    permission_classes = [CanModerate]

    def post(self, request, pk):
        lang = get_lang(request)
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return api_response(
                message_fr='Cours introuvable.',
                message_en='Course not found.',
                success=False, status_code=status.HTTP_404_NOT_FOUND, lang=lang,
            )

        if ModerationReview.objects.filter(moderator=request.user, course=course).exists():
            return api_response(
                message_fr='Vous avez déjà soumis un avis sur ce cours.',
                message_en='You already submitted a review for this course.',
                success=False, status_code=status.HTTP_400_BAD_REQUEST, lang=lang,
            )

        serializer = ModerationReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(moderator=request.user, course=course)

        # Si admin → décision finale immédiate
        if request.user.role == 'admin':
            _apply_final_decision(course, review.decision, review.comment)
        else:
            # 2 avis de modérateurs pairs → consensus
            reviews = ModerationReview.objects.filter(course=course)
            approvals = reviews.filter(decision='approve').count()
            rejections = reviews.filter(decision='reject').count()
            if approvals >= 2:
                _apply_final_decision(course, 'approve', '')
            elif rejections >= 2:
                _apply_final_decision(course, 'reject',
                                      review.comment or 'Rejeté après examen par pairs.')

        return api_response(
            message_fr='Avis de modération enregistré.',
            message_en='Moderation review submitted.',
            lang=lang,
        )


def _apply_final_decision(course, decision, reason):
    if decision == 'approve':
        course.status = 'approved'
        course.rejection_reason = ''
        course.save(update_fields=['status', 'rejection_reason'])
        grant_reputation(
            course.instructor, 'course_approved',
            description_fr=f'Cours approuvé : « {course.title} »',
            description_en=f'Course approved: "{course.title}"',
        )
        # Marquer les signalements comme invalides
        from .models import Report
        Report.objects.filter(course=course).update(is_valid=False, reviewed_at=timezone.now())
    else:
        course.status = 'rejected'
        course.rejection_reason = reason
        course.save(update_fields=['status', 'rejection_reason'])
        # Valider les signalements et récompenser les signaleurs
        from .models import Report
        reports = Report.objects.filter(course=course, is_valid__isnull=True)
        for report in reports:
            report.is_valid = True
            report.reviewed_at = timezone.now()
            report.save(update_fields=['is_valid', 'reviewed_at'])
            grant_reputation(
                report.reporter, 'valid_report',
                description_fr='Signalement validé par un modérateur',
                description_en='Report validated by moderator',
            )
