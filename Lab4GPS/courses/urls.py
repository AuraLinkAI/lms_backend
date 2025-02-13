from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from . import views

# Existing router setup for course endpoints
router = DefaultRouter()
router.register('', views.CourseViewSet, basename='courses')
router.register('assignments', views.AssignmentViewSet, basename='assignments')
router.register('submissions', views.AssignmentSubmissionViewSet, basename='submissions')
router.register('enrollments', views.EnrollmentViewSet, basename='enrollments')
router.register('progress', views.ModuleProgressViewSet, basename='progress')
router.register('wishlist', views.WishlistViewSet, basename='wishlist')

# Nested router for modules within courses
courses_router = nested_routers.NestedSimpleRouter(router, '', lookup='course')
courses_router.register('modules', views.ModuleViewSet, basename='course-modules')

# Nested router for content, assignments, and progress within modules
modules_router = nested_routers.NestedSimpleRouter(courses_router, 'modules', lookup='module')
modules_router.register('content', views.ModuleContentViewSet, basename='module-content')
modules_router.register('assignments', views.AssignmentViewSet, basename='module-assignments')
modules_router.register('progress', views.ModuleProgressViewSet, basename='module-progress')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(courses_router.urls)),
    path('', include(modules_router.urls)),

    # New endpoints for menu components (dummy endpoints)
    path('menu/admin/dashboard/', views.admin_dashboard, name='menu-admin-dashboard'),
    path('menu/analytics/instructor/', views.instructor_analytics, name='menu-instructor-analytics'),
    path('menu/analytics/student/', views.student_analytics, name='menu-student-analytics'),
    path('menu/settings/', views.menu_settings, name='menu-settings'),
    path('menu/notifications/', views.menu_notifications, name='menu-notifications'),
    path('menu/help/', views.menu_help, name='menu-help'),
]
