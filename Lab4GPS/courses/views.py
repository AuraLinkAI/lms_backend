from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import (
    Course, Module, ModuleContent, 
    Assignment, AssignmentSubmission, Enrollment, ModuleProgress, Wishlist
)
from .serializers import (
    CourseSerializer, ModuleSerializer, ModuleContentSerializer,
    AssignmentSerializer, AssignmentSubmissionSerializer, EnrollmentSerializer,
    ModuleProgressSerializer, WishlistSerializer
)
from .permissions import IsInstructor, IsStudent, IsAdmin

# ---------------------------
# Existing viewsets (unchanged)
# ---------------------------

from .permissions import IsInstructorOrAdmin, IsStudent, IsAdmin

from .permissions import IsInstructorOrAdmin, IsStudent, IsAdmin

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.prefetch_related('modules').select_related('instructor')
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsInstructorOrAdmin()]
        elif self.action == 'my_courses':
            return [IsInstructorOrAdmin()]  # Allow instructors and admins to view their courses
        elif self.action in ['in_progress_courses', 'completed_courses']:
            return [IsStudent()]
        else:
            return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsInstructorOrAdmin])
    def my_courses(self, request):
        courses = self.queryset.filter(instructor=request.user)
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsStudent])
    def in_progress_courses(self, request):
        courses = self.queryset.filter(
            assignments__submissions__student=request.user,
            assignments__submissions__grade__isnull=True
        ).distinct()
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsStudent])
    def completed_courses(self, request):
        courses = self.queryset.filter(
            assignments__submissions__student=request.user,
            assignments__submissions__grade__isnull=False
        ).distinct()
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)

class ModuleViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsStudent | IsInstructor | IsAdmin]
    serializer_class = ModuleSerializer

    def get_queryset(self):
        queryset = Module.objects.select_related('course').prefetch_related('contents', 'assignments').order_by('order')
        course_id = self.kwargs.get('course_pk')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def detailed_view(self, request, course_pk=None, pk=None):
        module = get_object_or_404(Module, course_id=course_pk, id=pk)
        serializer = self.get_serializer(module)
        return Response(serializer.data)


class ModuleContentViewSet(viewsets.ModelViewSet):
    queryset = ModuleContent.objects.all().select_related('module')
    serializer_class = ModuleContentSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructor | IsAdmin]

    def perform_create(self, serializer):
        module_id = self.kwargs.get('module_pk')
        serializer.save(module_id=module_id)


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all().select_related('module')
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructor | IsAdmin]

    def perform_create(self, serializer):
        module_id = self.kwargs.get('module_pk')
        serializer.save(module_id=module_id)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.all().select_related('assignment', 'student')
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def perform_create(self, serializer):
        assignment_id = self.kwargs.get('assignment_pk')
        serializer.save(student=self.request.user, assignment_id=assignment_id)

    @action(detail=False, methods=['get'], permission_classes=[IsStudent])
    def my_submissions(self, request):
        submissions = self.queryset.filter(student=request.user)
        serializer = self.get_serializer(submissions, many=True)
        return Response(serializer.data)


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ModuleProgressViewSet(viewsets.ModelViewSet):
    queryset = ModuleProgress.objects.all().select_related('module', 'user')
    serializer_class = ModuleProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.profile.role in ['admin']:
            return ModuleProgress.objects.all()
        return ModuleProgress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


# ---------------------------
# New endpoints for menu components
# ---------------------------

@api_view(['GET'])
def admin_dashboard(request):
    """Dummy endpoint for Admin Dashboard menu component."""
    data = {
        "totalUsers": 150,
        "activeUsers": 120,
        "pendingRequests": 5,
        "revenue": 5000,
    }
    return Response(data)


@api_view(['GET'])
def instructor_analytics(request):
    """Dummy endpoint for Instructor Analytics menu component."""
    data = {
        "totalCourses": 10,
        "totalStudents": 200,
        "averageRating": 4.5,
    }
    return Response(data)


@api_view(['GET'])
def student_analytics(request):
    """Dummy endpoint for Student Analytics menu component."""
    data = {
        "coursesEnrolled": 5,
        "completedCourses": 3,
        "progressPercentage": 70,
    }
    return Response(data)


@api_view(['GET', 'POST'])
def menu_settings(request):
    """Dummy endpoint for Settings menu component. GET returns dummy settings;
    POST echoes back updated settings."""
    dummy_settings = {"theme": "light", "notifications": True, "language": "en"}
    if request.method == 'GET':
        return Response(dummy_settings)
    elif request.method == 'POST':
        new_settings = request.data
        return Response({
            "message": "Settings updated successfully",
            "settings": new_settings
        })


@api_view(['GET'])
def menu_notifications(request):
    """Dummy endpoint for Notifications menu component."""
    data = [
        {"id": 1, "message": "System maintenance scheduled for tonight at 11 PM."},
        {"id": 2, "message": "New course materials available for your enrolled courses."},
        {"id": 3, "message": "Your profile has been updated successfully."},
    ]
    return Response(data)


@api_view(['GET'])
def menu_help(request):
    """Dummy endpoint for Help menu component."""
    data = [
        {"id": 1, "title": "How to navigate the platform", "content": "Use the menu to access different features."},
        {"id": 2, "title": "Troubleshooting common issues", "content": "Clear cache and restart your browser."},
        {"id": 3, "title": "Contact support", "content": "Email support@example.com for further assistance."},
    ]
    return Response(data)

class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)