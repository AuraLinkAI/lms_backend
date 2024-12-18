from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, ModuleViewSet, ModuleContentViewSet,
    AssignmentViewSet, AssignmentSubmissionViewSet
)

router = DefaultRouter()
router.register('courses', CourseViewSet)
router.register('modules', ModuleViewSet)
router.register('module-content', ModuleContentViewSet)
router.register('assignments', AssignmentViewSet)
router.register('submissions', AssignmentSubmissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
