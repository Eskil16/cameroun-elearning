from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='following_set', verbose_name=_('abonné')
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='followers_set', verbose_name=_('suivi')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = _('abonnement')
        verbose_name_plural = _('abonnements')

    def __str__(self):
        return f"{self.follower} → {self.following}"


class FeedItem(models.Model):
    TYPE_COURSE_PUBLISHED = 'course_published'
    TYPE_BADGE_EARNED = 'badge_earned'
    TYPE_COURSE_COMPLETED = 'course_completed'
    TYPE_COMMENT = 'comment'
    TYPE_CHOICES = [
        (TYPE_COURSE_PUBLISHED, _('Cours publié')),
        (TYPE_BADGE_EARNED, _('Badge obtenu')),
        (TYPE_COURSE_COMPLETED, _('Cours terminé')),
        (TYPE_COMMENT, _('Commentaire')),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='feed_actions', verbose_name=_('acteur')
    )
    item_type = models.CharField(
        _('type'), max_length=30, choices=TYPE_CHOICES
    )
    content_fr = models.TextField(_('contenu (fr)'))
    content_en = models.TextField(_('contenu (en)'), blank=True)
    course = models.ForeignKey(
        'courses.Course', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='feed_items'
    )
    badge = models.ForeignKey(
        'reputation.Badge', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('fil d\'actualité')
        verbose_name_plural = _('fils d\'actualité')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.actor} – {self.item_type}"


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='likes'
    )
    feed_item = models.ForeignKey(
        FeedItem, on_delete=models.CASCADE, related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'feed_item')
