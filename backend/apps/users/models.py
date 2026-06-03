from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    ROLE_STUDENT = 'student'
    ROLE_INSTRUCTOR = 'instructor'
    ROLE_MODERATOR = 'moderator'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_STUDENT, _('Étudiant / Student')),
        (ROLE_INSTRUCTOR, _('Formateur / Instructor')),
        (ROLE_MODERATOR, _('Modérateur / Moderator')),
        (ROLE_ADMIN, _('Administrateur / Admin')),
    ]

    LANG_FR = 'fr'
    LANG_EN = 'en'
    LANG_CHOICES = [
        (LANG_FR, 'Français'),
        (LANG_EN, 'English'),
    ]

    email = models.EmailField(_('email'), unique=True)
    phone_number = models.CharField(
        _('numéro de téléphone'), max_length=20, blank=True,
        help_text=_('Optionnel — pour alertes SMS en cas de panne')
    )
    bio = models.TextField(_('biographie'), max_length=500, blank=True)
    avatar = models.ImageField(
        _('avatar'), upload_to='avatars/', null=True, blank=True
    )
    preferred_language = models.CharField(
        _('langue préférée'), max_length=2,
        choices=LANG_CHOICES, default=LANG_FR
    )
    role = models.CharField(
        _('rôle'), max_length=20,
        choices=ROLE_CHOICES, default=ROLE_STUDENT
    )
    reputation_score = models.IntegerField(_('score de réputation'), default=0)
    is_verified = models.BooleanField(_('vérifié'), default=False)
    verification_code = models.CharField(max_length=6, blank=True)
    skills = models.TextField(_('compétences'), blank=True,
                              help_text=_('Séparées par des virgules'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def trust_score_display(self):
        if self.reputation_score >= 500:
            return '★★★★★'
        elif self.reputation_score >= 200:
            return '★★★★'
        elif self.reputation_score >= 100:
            return '★★★'
        elif self.reputation_score >= 50:
            return '★★'
        elif self.reputation_score >= 10:
            return '★'
        return '☆'

    def can_moderate(self):
        return self.reputation_score >= 100 or self.role in (
            self.ROLE_MODERATOR, self.ROLE_ADMIN
        )
