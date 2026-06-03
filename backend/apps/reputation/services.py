from django.conf import settings
from .models import ReputationEvent, Badge, UserBadge


POINTS_MAP = {
    'course_approved': settings.REPUTATION_COURSE_APPROVED,
    'like_received': settings.REPUTATION_LIKE_RECEIVED,
    'valid_report': settings.REPUTATION_VALID_REPORT,
}


def grant_reputation(user, event_type, points=None, description_fr='', description_en=''):
    if points is None:
        points = POINTS_MAP.get(event_type, 0)
    if points == 0:
        return

    ReputationEvent.objects.create(
        user=user,
        event_type=event_type,
        points=points,
        description_fr=description_fr,
        description_en=description_en,
    )
    user.reputation_score += points
    user.save(update_fields=['reputation_score'])
    check_and_award_badges(user)


def check_and_award_badges(user):
    eligible = Badge.objects.filter(
        required_score__lte=user.reputation_score,
        is_special=False,
    ).exclude(
        slug__in=user.badges.values_list('badge__slug', flat=True)
    )
    for badge in eligible:
        UserBadge.objects.create(user=user, badge=badge)
        from apps.social.models import FeedItem
        FeedItem.objects.create(
            actor=user,
            item_type='badge_earned',
            content_fr=f'a obtenu le badge « {badge.name_fr} » {badge.icon}',
            content_en=f'earned the badge "{badge.name_en}" {badge.icon}',
            badge=badge,
        )

    special_badges_check(user)


def special_badges_check(user):
    """Badges spéciaux Cameroun basés sur des critères métier."""
    earned_slugs = set(user.badges.values_list('badge__slug', flat=True))

    # Champion de la data : a publié des cours uniquement faible bande passante
    if 'champion-data' not in earned_slugs:
        courses = user.courses_created.filter(status='approved')
        if courses.exists() and all(c.is_low_bandwidth for c in courses):
            try:
                badge = Badge.objects.get(slug='champion-data')
                UserBadge.objects.get_or_create(user=user, badge=badge)
            except Badge.DoesNotExist:
                pass

    # Prof hors ligne : a des modules téléchargeables
    if 'prof-hors-ligne' not in earned_slugs:
        from apps.courses.models import Module
        downloadable = Module.objects.filter(
            course__instructor=user, is_downloadable=True
        ).exists()
        if downloadable:
            try:
                badge = Badge.objects.get(slug='prof-hors-ligne')
                UserBadge.objects.get_or_create(user=user, badge=badge)
            except Badge.DoesNotExist:
                pass

    # Mentor bilangue : a des cours en mode 'both'
    if 'mentor-bilangue' not in earned_slugs:
        bilingual = user.courses_created.filter(
            status='approved', language='both'
        ).exists()
        if bilingual:
            try:
                badge = Badge.objects.get(slug='mentor-bilangue')
                UserBadge.objects.get_or_create(user=user, badge=badge)
            except Badge.DoesNotExist:
                pass
