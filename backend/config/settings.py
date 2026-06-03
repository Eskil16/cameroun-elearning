"""
Django settings — Réseau Académique Camerounais
Timezone: Africa/Douala | Langues: fr, en
Compatible Railway (DATABASE_URL, PORT auto)
"""
import os
import dj_database_url
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-changeme-in-production-!!')

DEBUG = config('DEBUG', default=False, cast=bool)

# Sur Railway : accepte tous les hôtes (le domaine est dynamique)
# En local : restreindre via la variable ALLOWED_HOSTS du .env
DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL:
    # Mode Railway/Production : domaine inconnu à l'avance
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Tiers
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    # Locales
    'apps.users',
    'apps.courses',
    'apps.social',
    'apps.moderation',
    'apps.reputation',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Sert le frontend HTML depuis Django
        'DIRS': [BASE_DIR.parent / 'frontend'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ── Base de données ────────────────────────────────────────────────────────────
# Railway fournit DATABASE_URL automatiquement quand PostgreSQL est attaché

if DATABASE_URL:
    # Mode Railway / Production : utilise DATABASE_URL
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Mode développement local : PostgreSQL classique
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql',
            'NAME':     config('DB_NAME',     default='cameroun_elearning'),
            'USER':     config('DB_USER',     default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default='postgres'),
            'HOST':     config('DB_HOST',     default='localhost'),
            'PORT':     config('DB_PORT',     default='5432'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalisation ───────────────────────────────────────────────────────
LANGUAGE_CODE = 'fr'
LANGUAGES = [('fr', 'Français'), ('en', 'English')]
TIME_ZONE  = 'Africa/Douala'
USE_I18N   = True
USE_L10N   = True
USE_TZ     = True
LOCALE_PATHS = [BASE_DIR / 'locale']

# ── Fichiers statiques ─────────────────────────────────────────────────────────
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Whitenoise sert aussi le frontend JS/CSS en production
WHITENOISE_ROOT = BASE_DIR.parent / 'frontend'

# ── Médias (uploads) ───────────────────────────────────────────────────────────
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Limites upload ─────────────────────────────────────────────────────────────
DATA_UPLOAD_MAX_MEMORY_SIZE = 314572800   # 300 Mo
FILE_UPLOAD_MAX_MEMORY_SIZE = 314572800
MAX_VIDEO_SIZE  = 314572800   # 300 Mo
MAX_PDF_SIZE    = 20971520    # 20 Mo
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/webm', 'video/ogg']
ALLOWED_PDF_TYPES   = ['application/pdf']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL    = 'users.User'

# ── Django REST Framework ──────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'EXCEPTION_HANDLER': 'apps.users.utils.custom_exception_handler',
}

# ── JWT ────────────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS':  True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# ── CORS ───────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True   # Railway : domaine généré dynamiquement
CORS_ALLOW_CREDENTIALS = True

# ── Réputation ─────────────────────────────────────────────────────────────────
REPUTATION_COURSE_APPROVED  = 10
REPUTATION_LIKE_RECEIVED    = 1
REPUTATION_VALID_REPORT     = 2
REPUTATION_MODERATOR_THRESHOLD = 100
REPORT_QUARANTINE_THRESHOLD = 3

# ── Email ──────────────────────────────────────────────────────────────────────
EMAIL_BACKEND   = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST      = config('EMAIL_HOST',    default='smtp.gmail.com')
EMAIL_PORT      = config('EMAIL_PORT',    default=587, cast=int)
EMAIL_USE_TLS   = True
EMAIL_HOST_USER     = config('EMAIL_HOST_USER',     default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL  = config('DEFAULT_FROM_EMAIL',  default='noreply@elearning.cm')

# ── Sécurité production ────────────────────────────────────────────────────────
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT     = False   # Railway gère le SSL en amont
    SESSION_COOKIE_SECURE   = True
    CSRF_COOKIE_SECURE      = True
    SECURE_HSTS_SECONDS     = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
