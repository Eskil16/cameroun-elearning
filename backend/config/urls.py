from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.generic import TemplateView


def health_check(request):
    """Endpoint de santé pour Railway."""
    return JsonResponse({'status': 'ok', 'platform': 'Réseau Académique Camerounais'})


urlpatterns = [
    path('admin/', admin.site.urls),

    # Health check Railway
    path('health/', health_check, name='health'),

    # API v1
    path('api/v1/auth/',       include('apps.users.urls_auth')),
    path('api/v1/users/',      include('apps.users.urls')),
    path('api/v1/courses/',    include('apps.courses.urls')),
    path('api/v1/social/',     include('apps.social.urls')),
    path('api/v1/moderation/', include('apps.moderation.urls')),
    path('api/v1/reputation/', include('apps.reputation.urls')),

    # Frontend — toutes les pages HTML servies par Django/Whitenoise
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login',       TemplateView.as_view(template_name='login.html')),
    path('register',    TemplateView.as_view(template_name='register.html')),
    path('profile',     TemplateView.as_view(template_name='profile.html')),
    path('course',      TemplateView.as_view(template_name='course_detail.html')),
    path('create',      TemplateView.as_view(template_name='create_course.html')),
    path('moderation',  TemplateView.as_view(template_name='dashboard_moderator.html')),
    path('feed',        TemplateView.as_view(template_name='feed.html')),
    path('offline',     TemplateView.as_view(template_name='offline.html')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
