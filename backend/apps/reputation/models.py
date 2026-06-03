from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Badge(models.Model):
    slug = models.SlugField(unique=True)
    name_fr = models.CharField(_('nom (fr)'), max_length=100)
    name_en = models.CharField(_('name (en)'), max_length=100)
    description_fr = models.TextField()
    description_en = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='🏆')
    required_score = models.IntegerField(default=0)
    is_special = models.BooleanField(
        default=False,
        help_text=_('Badge spécial Cameroun (local)')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('badge')
        ordering = ['required_score']

    def __str__(self):
        return self.name_fr

    def get_name(self, lang='fr'):
        return self.name_fr if lang == 'fr' else self.name_en


class UserBadge(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='badges'
    )
    badge = models.ForeignKey(
        Badge, on_delete=models.CASCADE, related_name='user_badges'
    )
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')
        verbose_name = _('badge utilisateur')
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.user} – {self.badge}"


class ReputationEvent(models.Model):
    EVENT_COURSE_APPROVED = 'course_approved'
    EVENT_LIKE_RECEIVED = 'like_received'
    EVENT_VALID_REPORT = 'valid_report'
    EVENT_BADGE_EARNED = 'badge_earned'
    EVENT_CHOICES = [
        (EVENT_COURSE_APPROVED, _('Cours approuvé (+10)')),
        (EVENT_LIKE_RECEIVED, _('Like reçu (+1)')),
        (EVENT_VALID_REPORT, _('Signalement validé (+2)')),
        (EVENT_BADGE_EARNED, _('Badge obtenu')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reputation_events'
    )
    event_type = models.CharField(
        _('type d\'événement'), max_length=30, choices=EVENT_CHOICES
    )
    points = models.IntegerField(_('points'), default=0)
    description_fr = models.CharField(max_length=200, blank=True)
    description_en = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('événement de réputation')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} | {self.event_type} | {self.points:+d} pts"
