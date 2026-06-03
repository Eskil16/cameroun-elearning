from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'get_full_name', 'role', 'reputation_score', 'is_verified']
    list_filter = ['role', 'is_verified', 'preferred_language']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Profil Académique', {
            'fields': ('phone_number', 'bio', 'avatar', 'preferred_language',
                       'role', 'reputation_score', 'is_verified', 'skills')
        }),
    )
