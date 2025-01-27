from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StampViewSet, DocumentViewSet

router = DefaultRouter()
router.register('stamps', StampViewSet, basename='stamp')
router.register('documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
]
