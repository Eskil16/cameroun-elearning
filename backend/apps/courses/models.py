from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name_fr = models.CharField(_('nom (fr)'), max_length=100)
    name_en = models.CharField(_('name (en)'), max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='📚')
    description_fr = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('catégorie')
        verbose_name_plural = _('catégories')
        ordering = ['name_fr']

    def __str__(self):
        return self.name_fr

    def get_name(self, lang='fr'):
        return self.name_fr if lang == 'fr' else self.name_en


class Course(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_QUARANTINE = 'quarantine'
    STATUS_CHOICES = [
        (STATUS_PENDING, _('En attente / Pending')),
        (STATUS_APPROVED, _('Approuvé / Approved')),
        (STATUS_REJECTED, _('Rejeté / Rejected')),
        (STATUS_QUARANTINE, _('Quarantaine / Quarantine')),
    ]

    LEVEL_BEGINNER = 'beginner'
    LEVEL_INTERMEDIATE = 'intermediate'
    LEVEL_EXPERT = 'expert'
    LEVEL_CHOICES = [
        (LEVEL_BEGINNER, _('Débutant / Beginner')),
        (LEVEL_INTERMEDIATE, _('Intermédiaire / Intermediate')),
        (LEVEL_EXPERT, _('Expert')),
    ]

    LANG_FR = 'fr'
    LANG_EN = 'en'
    LANG_BOTH = 'both'
    LANG_CHOICES = [
        (LANG_FR, 'Français'),
        (LANG_EN, 'English'),
        (LANG_BOTH, 'Bilingue / Bilingual'),
    ]

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='courses_created', verbose_name=_('formateur')
    )
    title = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, related_name='courses'
    )
    level = models.CharField(
        _('niveau'), max_length=20,
        choices=LEVEL_CHOICES, default=LEVEL_BEGINNER
    )
    language = models.CharField(
        _('langue'), max_length=10,
        choices=LANG_CHOICES, default=LANG_FR
    )
    status = models.CharField(
        _('statut'), max_length=20,
        choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    rejection_reason = models.TextField(_('motif de rejet'), blank=True)
    thumbnail = models.ImageField(
        _('miniature'), upload_to='thumbnails/', null=True, blank=True
    )
    is_low_bandwidth = models.BooleanField(
        _('faible bande passante'), default=False,
        help_text=_('Coché automatiquement si tous les modules < 50 Mo')
    )
    total_size_mb = models.FloatField(_('taille totale (Mo)'), default=0)
    report_count = models.IntegerField(_('signalements'), default=0)
    enrollment_count = models.IntegerField(_('inscriptions'), default=0)
    average_rating = models.FloatField(_('note moyenne'), default=0.0)
    rating_count = models.IntegerField(_('nombre de notes'), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('cours')
        verbose_name_plural = _('cours')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def update_rating(self):
        from django.db.models import Avg, Count
        result = self.ratings.aggregate(avg=Avg('stars'), cnt=Count('id'))
        self.average_rating = result['avg'] or 0.0
        self.rating_count = result['cnt'] or 0
        self.save(update_fields=['average_rating', 'rating_count'])

    def update_size(self):
        total = sum(m.file_size_mb for m in self.modules.all())
        self.total_size_mb = total
        self.is_low_bandwidth = total < 50
        self.save(update_fields=['total_size_mb', 'is_low_bandwidth'])


class Module(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE,
        related_name='modules', verbose_name=_('cours')
    )
    title = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    order = models.PositiveSmallIntegerField(_('ordre'), default=0)
    video = models.FileField(
        _('vidéo'), upload_to='videos/', null=True, blank=True
    )
    pdf = models.FileField(
        _('PDF'), upload_to='pdfs/', null=True, blank=True
    )
    video_compressed = models.FileField(
        _('vidéo compressée'), upload_to='videos/compressed/',
        null=True, blank=True
    )
    duration_minutes = models.PositiveIntegerField(
        _('durée (min)'), default=0
    )
    file_size_mb = models.FloatField(_('taille (Mo)'), default=0)
    is_downloadable = models.BooleanField(
        _('téléchargeable hors ligne'), default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('module')
        verbose_name_plural = _('modules')
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} – Module {self.order}: {self.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = _('inscription')
        verbose_name_plural = _('inscriptions')


class Progress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='progress'
    )
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name='progress'
    )
    percentage = models.FloatField(
        _('pourcentage'), default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    last_position_seconds = models.IntegerField(
        _('dernière position (s)'), default=0
    )
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'module')
        verbose_name = _('progression')
        verbose_name_plural = _('progressions')


class CourseRating(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='ratings'
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='ratings'
    )
    stars = models.PositiveSmallIntegerField(
        _('étoiles'),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(_('commentaire'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = _('évaluation')
        verbose_name_plural = _('évaluations')
        ordering = ['-created_at']
