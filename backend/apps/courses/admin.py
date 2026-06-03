from django.contrib import admin
from .models import Category, Course, Module, Enrollment, CourseRating


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_fr', 'name_en', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name_fr',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'status', 'level',
                    'is_low_bandwidth', 'average_rating', 'enrollment_count']
    list_filter = ['status', 'level', 'language', 'is_low_bandwidth', 'category']
    search_fields = ['title', 'description', 'instructor__email']
    actions = ['approve_courses', 'reject_courses']

    def approve_courses(self, request, queryset):
        from apps.reputation.services import grant_reputation
        for course in queryset.filter(status__in=['pending', 'quarantine']):
            course.status = 'approved'
            course.save(update_fields=['status'])
            grant_reputation(course.instructor, 'course_approved',
                             description_fr=f'Cours approuvé : {course.title}',
                             description_en=f'Course approved: {course.title}')
        self.message_user(request, 'Cours approuvés avec succès.')
    approve_courses.short_description = 'Approuver les cours sélectionnés'

    def reject_courses(self, request, queryset):
        queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, 'Cours rejetés.')
    reject_courses.short_description = 'Rejeter les cours sélectionnés'


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'file_size_mb', 'is_downloadable']
    list_filter = ['is_downloadable']


admin.site.register(Enrollment)
admin.site.register(CourseRating)
