from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Course, Module, ModuleContent, Assignment, AssignmentSubmission
from .serializers import (
    CourseSerializer, ModuleSerializer, ModuleContentSerializer,
    AssignmentSerializer, AssignmentSubmissionSerializer
)
from .permissions import IsInstructor, IsStudent, IsAdmin


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing courses with custom actions for instructors and students.
    """
    queryset = Course.objects.all().select_related('instructor').prefetch_related('modules__contents', 'modules__assignments')
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Assign the currently logged-in user as the instructor when creating a course.
        """
        serializer.save(instructor=self.request.user)

    @action(detail=False, methods=['get'], url_path='my-courses', permission_classes=[IsInstructor])
    def my_courses(self, request):
        """
        Custom action for instructors to view their courses.
        """
        courses = self.queryset.filter(instructor=request.user)
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='in-progress', permission_classes=[IsStudent])
    def in_progress_courses(self, request):
        """
        Custom action for students to view courses with pending assignments.
        """
        courses = self.queryset.filter(
            assignments__submissions__student=request.user,
            assignments__submissions__grade__isnull=True
        ).distinct()
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='completed', permission_classes=[IsStudent])
    def completed_courses(self, request):
        """
        Custom action for students to view courses with completed assignments.
        """
        courses = self.queryset.filter(
            assignments__submissions__student=request.user,
            assignments__submissions__grade__isnull=False
        ).distinct()
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)


class ModuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing modules within a course.
    """
    queryset = Module.objects.all().select_related('course').prefetch_related('contents', 'assignments')
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructor | IsAdmin]

    def perform_create(self, serializer):
        """
        Ensure the module is associated with an existing course.
        """
        serializer.save()


class ModuleContentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing content within modules.
    """
    queryset = ModuleContent.objects.all().select_related('module')
    serializer_class = ModuleContentSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructor | IsAdmin]

    def perform_create(self, serializer):
        """
        Add content to a specific module.
        """
        serializer.save()


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing assignments within a module.
    """
    queryset = Assignment.objects.all().select_related('module')
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructor | IsAdmin]

    def perform_create(self, serializer):
        """
        Add assignments to a module.
        """
        serializer.save()


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing assignment submissions by students.
    """
    queryset = AssignmentSubmission.objects.all().select_related('assignment', 'student')
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Allow students to submit their assignments.
        """
        serializer.save(student=self.request.user)

    @action(detail=False, methods=['get'], url_path='my-submissions', permission_classes=[IsStudent])
    def my_submissions(self, request):
        """
        Custom action for students to view their submissions.
        """
        submissions = self.queryset.filter(student=request.user)
        serializer = self.get_serializer(submissions, many=True)
        return Response(serializer.data)
