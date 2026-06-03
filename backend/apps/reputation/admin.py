from django.contrib import admin
from .models import Badge, UserBadge, ReputationEvent


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name_fr', 'name_en', 'icon', 'required_score', 'is_special']
    list_filter = ['is_special']
    prepopulated_fields = {}


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at']
    list_filter = ['badge']


@admin.register(ReputationEvent)
class ReputationEventAdmin(admin.ModelAdmin):
    list_display = ['user', 'event_type', 'points', 'created_at']
    list_filter = ['event_type']
