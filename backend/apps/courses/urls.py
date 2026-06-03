from django.urls import path
from .views import (
    CategoryListView,
    CourseListView, CourseCreateView, CourseDetailView, MyCourseListView,
    ModuleListCreateView, ModuleDetailView,
    EnrollView, MyEnrollmentsView,
    UpdateProgressView,
    CourseRatingView,
)

urlpatterns = [
    path('', CourseListView.as_view(), name='course-list'),
    path('create/', CourseCreateView.as_view(), name='course-create'),
    path('my/', MyCourseListView.as_view(), name='course-my'),
    path('enrolled/', MyEnrollmentsView.as_view(), name='course-enrolled'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('<int:pk>/enroll/', EnrollView.as_view(), name='course-enroll'),
    path('<int:pk>/rate/', CourseRatingView.as_view(), name='course-rate'),
    path('<int:course_pk>/modules/', ModuleListCreateView.as_view(), name='module-list'),
    path('modules/<int:pk>/', ModuleDetailView.as_view(), name='module-detail'),
    path('modules/<int:module_pk>/progress/', UpdateProgressView.as_view(), name='module-progress'),
]
