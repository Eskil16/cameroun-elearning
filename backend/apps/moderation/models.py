from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Report(models.Model):
    REASON_SPAM = 'spam'
    REASON_QUALITY = 'low_quality'
    REASON_FACTUAL = 'factual_error'
    REASON_INAPPROPRIATE = 'inappropriate'
    REASON_CHOICES = [
        (REASON_SPAM, _('Spam')),
        (REASON_QUALITY, _('Faible qualité / Low quality')),
        (REASON_FACTUAL, _('Erreur factuelle / Factual error')),
        (REASON_INAPPROPRIATE, _('Contenu inapproprié / Inappropriate')),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reports_filed', verbose_name=_('signaleur')
    )
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE,
        related_name='reports', verbose_name=_('cours')
    )
    reason = models.CharField(
        _('motif'), max_length=30, choices=REASON_CHOICES
    )
    details = models.TextField(_('détails'), blank=True)
    is_valid = models.BooleanField(
        _('signal valide'), null=True, blank=True
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reporter', 'course')
        verbose_name = _('signalement')
        verbose_name_plural = _('signalements')
        ordering = ['-created_at']

    def __str__(self):
        return f"Signal de {self.reporter} sur «{self.course.title}»"


class ModerationReview(models.Model):
    DECISION_APPROVE = 'approve'
    DECISION_REJECT = 'reject'
    DECISION_CHOICES = [
        (DECISION_APPROVE, _('Approuver / Approve')),
        (DECISION_REJECT, _('Rejeter / Reject')),
    ]

    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reviews', verbose_name=_('modérateur')
    )
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE,
        related_name='mod_reviews', verbose_name=_('cours')
    )
    decision = models.CharField(
        _('décision'), max_length=20, choices=DECISION_CHOICES
    )
    comment = models.TextField(_('commentaire'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('moderator', 'course')
        verbose_name = _('avis de modération')
        verbose_name_plural = _('avis de modération')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.moderator} → {self.course.title}: {self.decision}"
