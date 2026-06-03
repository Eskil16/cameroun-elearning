from django.urls import path
from .views import ModerationQueueView, ModerationReviewView, ReportCourseView

urlpatterns = [
    path('queue/', ModerationQueueView.as_view(), name='moderation-queue'),
    path('courses/<int:pk>/report/', ReportCourseView.as_view(), name='course-report'),
    path('courses/<int:pk>/review/', ModerationReviewView.as_view(), name='course-review'),
]
