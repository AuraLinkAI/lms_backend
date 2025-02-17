from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Wishlist
from .serializers import WishlistSerializer

# Wishlist View
class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Menu API Views
@api_view(["GET"])
def admin_dashboard(request):
    data = {
        "totalUsers": 150,
        "activeUsers": 120,
        "pendingRequests": 5,
        "revenue": 5000,
    }
    return Response(data)

@api_view(["GET"])
def instructor_analytics(request):
    data = {
        "totalCourses": 10,
        "totalStudents": 200,
        "averageRating": 4.5,
    }
    return Response(data)

@api_view(["GET"])
def student_analytics(request):
    data = {
        "coursesEnrolled": 5,
        "completedCourses": 3,
        "progressPercentage": 70,
    }
    return Response(data)

@api_view(["GET", "POST"])
def menu_settings(request):
    dummy_settings = {"theme": "light", "notifications": True, "language": "en"}
    if request.method == "GET":
        return Response(dummy_settings)
    elif request.method == "POST":
        new_settings = request.data
        return Response({"message": "Settings updated successfully", "settings": new_settings})

@api_view(["GET"])
def menu_notifications(request):
    data = [
        {"id": 1, "message": "System maintenance scheduled for tonight at 11 PM."},
        {"id": 2, "message": "New course materials available for your enrolled courses."},
        {"id": 3, "message": "Your profile has been updated successfully."},
    ]
    return Response(data)

@api_view(["GET"])
def menu_help(request):
    data = [
        {"id": 1, "title": "How to navigate the platform", "content": "Use the menu to access different features."},
        {"id": 2, "title": "Troubleshooting common issues", "content": "Clear cache and restart your browser."},
        {"id": 3, "title": "Contact support", "content": "Email support@example.com for further assistance."},
    ]
    return Response(data)
