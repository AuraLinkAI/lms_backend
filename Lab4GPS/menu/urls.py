# menu/urls.py or wishlist/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WishlistViewSet,
    admin_dashboard, instructor_analytics, student_analytics,
    menu_settings, menu_notifications, menu_help
)

router = DefaultRouter()
router.register("wishlist", WishlistViewSet, basename="wishlist")

urlpatterns = [
    path("", include(router.urls)),
    path("menu/admin/dashboard/", admin_dashboard, name="menu-admin-dashboard"),
    path("menu/analytics/instructor/", instructor_analytics, name="menu-instructor-analytics"),
    path("menu/analytics/student/", student_analytics, name="menu-student-analytics"),
    path("menu/settings/", menu_settings, name="menu-settings"),
    path("menu/notifications/", menu_notifications, name="menu-notifications"),
    path("menu/help/", menu_help, name="menu-help"),
]
