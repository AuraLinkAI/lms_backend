from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Avg
from django.contrib.auth import get_user_model

from .models import Wishlist
from .serializers import WishlistSerializer
from courses.models import Course, Enrollment
# If you track module progress:
# from courses.models import ModuleProgress

User = get_user_model()

class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# ----------------------------------
#         Admin Dashboard
# ----------------------------------
@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])  # or custom
def admin_dashboard(request):
    """
    Real data for admin dashboard:
      - totalUsers (# of users)
      - activeUsers (# of is_active)
      - pendingRequests (if you store them or 0 otherwise)
      - revenue => now omitted or set to 0 since no Payment model
    """
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()

    pending_requests = 0  # or logic if you track requests
    # e.g. from .models import InstructorRequest
    # pending_requests = InstructorRequest.objects.filter(status='pending').count()

    # No Payment logic => set to 0
    data = {
        "totalUsers": total_users,
        "activeUsers": active_users,
        "pendingRequests": pending_requests,
        "revenue": 0,  # Since you don't have payment
    }
    return Response(data)

# ----------------------------------
#       Instructor Analytics
# ----------------------------------
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def instructor_analytics(request):
    """
    For instructors:
      - totalCourses = # of courses taught by request.user
      - totalStudents = distinct # of students across those courses
      - (removed rating) => let's omit or return 0.0
    """
    # If you want to ensure user is actually an instructor:
    # if request.user.role != 'INSTRUCTOR':
    #     return Response({"detail": "Not an instructor"}, status=403)

    instructor_courses = Course.objects.filter(instructor=request.user)
    total_courses = instructor_courses.count()

    total_students = Enrollment.objects.filter(course__in=instructor_courses) \
                                       .values('user').distinct().count()

    data = {
        "totalCourses": total_courses,
        "totalStudents": total_students,
        # rating is omitted => we can do
        "averageRating": 0.0,
    }
    return Response(data)

# ----------------------------------
#       Student Analytics
# ----------------------------------
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def student_analytics(request):
    """
    For students:
      - coursesEnrolled => # of enrollments
      - completedCourses => # with status='completed'
      - progressPercentage => average from ModuleProgress if you have it; else 0
    """
    # if request.user.role != 'STUDENT':
    #    return Response({"detail": "Not a student"}, status=403)

    courses_enrolled = Enrollment.objects.filter(user=request.user).count()

    completed_courses = Enrollment.objects.filter(
        user=request.user, 
        status='completed'
    ).count()

    # If you don't have ModuleProgress, just do 0.
    # If you do, you can do:
    # from courses.models import ModuleProgress
    # progress_qs = ModuleProgress.objects.filter(user=request.user)
    # avg_progress = progress_qs.aggregate(val=Avg('progress'))['val'] or 0
    avg_progress = 0  # or real logic if you have progress

    data = {
        "coursesEnrolled": courses_enrolled,
        "completedCourses": completed_courses,
        "progressPercentage": int(avg_progress),
    }
    return Response(data)

# ----------------------------------
#       Settings Endpoint
# ----------------------------------
@api_view(["GET", "POST"])
@permission_classes([permissions.IsAuthenticated])
def menu_settings(request):
    """
    If you store user settings in DB, do real queries. 
    Otherwise keep dummy or partial logic.
    """
    dummy_settings = {"theme": "light", "notifications": True, "language": "en"}
    if request.method == "GET":
        return Response(dummy_settings)
    elif request.method == "POST":
        new_settings = request.data
        return Response({
            "message": "Settings updated successfully",
            "settings": new_settings
        })

# ----------------------------------
#       Notifications Endpoint
# ----------------------------------
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def menu_notifications(request):
    """
    If you have a Notification model, query it. 
    Otherwise keep dummy data or partial logic.
    """
    data = [
        {"id": 1, "message": "System maintenance scheduled for tonight at 11 PM."},
        {"id": 2, "message": "New course materials available for your enrolled courses."},
        {"id": 3, "message": "Your profile has been updated successfully."},
    ]
    return Response(data)

# ----------------------------------
#       Help Endpoint
# ----------------------------------
@api_view(["GET"])
def menu_help(request):
    """
    If you have a HelpTopic model, query it.
    Otherwise keep dummy data.
    """
    data = [
        {"id": 1, "title": "How to navigate the platform", "content": "Use the menu to access different features."},
        {"id": 2, "title": "Troubleshooting common issues", "content": "Clear cache and restart your browser."},
        {"id": 3, "title": "Contact support", "content": "Email support@example.com for further assistance."},
    ]
    return Response(data)
