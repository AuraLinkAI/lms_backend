# courses/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from .views import (
    CourseViewSet, ModuleViewSet, ModuleContentViewSet,
    AssignmentViewSet, AssignmentSubmissionViewSet, EnrollmentViewSet,
    ModuleProgressViewSet
)

# Main router setup
router = DefaultRouter()
router.register('', CourseViewSet, basename='courses')  # Register at the root of 'courses/'
router.register('assignments', AssignmentViewSet, basename='assignments')
router.register('submissions', AssignmentSubmissionViewSet, basename='submissions')
router.register('enrollments', EnrollmentViewSet, basename='enrollments')
router.register('progress', ModuleProgressViewSet, basename='progress')  # Added for ModuleProgress

# Nested router setup for modules within courses
courses_router = nested_routers.NestedSimpleRouter(router, '', lookup='course')  # Lookup 'course'
courses_router.register('modules', ModuleViewSet, basename='course-modules')

# Nested router setup for content within modules
modules_router = nested_routers.NestedSimpleRouter(courses_router, 'modules', lookup='module')
modules_router.register('content', ModuleContentViewSet, basename='module-content')
modules_router.register('assignments', AssignmentViewSet, basename='module-assignments')
modules_router.register('progress', ModuleProgressViewSet, basename='module-progress')  # Added nested progress

# Include URLs from main and nested routers
urlpatterns = [
    path('', include(router.urls)),              # Main router
    path('', include(courses_router.urls)),     # Nested courses router
    path('', include(modules_router.urls)),     # Nested modules router
]
