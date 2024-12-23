from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from .views import (
    CourseViewSet, ModuleViewSet, ModuleContentViewSet,
    AssignmentViewSet, AssignmentSubmissionViewSet, EnrollmentViewSet
)

# Main router setup
router = DefaultRouter()
router.register('courses', CourseViewSet)
router.register('assignments', AssignmentViewSet)
router.register('submissions', AssignmentSubmissionViewSet)
router.register('enrollments', EnrollmentViewSet)

# Nested router setup for modules within courses
courses_router = nested_routers.NestedSimpleRouter(router, 'courses', lookup='course')
courses_router.register('modules', ModuleViewSet, basename='course-modules')

# Nested router setup for content within modules
modules_router = nested_routers.NestedSimpleRouter(courses_router, 'modules', lookup='module')
modules_router.register('content', ModuleContentViewSet, basename='module-content')

# Include URLs from main and nested routers
urlpatterns = [
    path('', include(router.urls)),
    path('', include(courses_router.urls)),
    path('', include(modules_router.urls)),
]
