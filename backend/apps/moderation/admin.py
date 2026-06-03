from django.contrib import admin
from .models import Report, ModerationReview


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'course', 'reason', 'is_valid', 'created_at']
    list_filter = ['reason', 'is_valid']
    search_fields = ['course__title', 'reporter__email']


@admin.register(ModerationReview)
class ModerationReviewAdmin(admin.ModelAdmin):
    list_display = ['moderator', 'course', 'decision', 'created_at']
    list_filter = ['decision']
