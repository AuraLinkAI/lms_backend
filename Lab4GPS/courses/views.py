# courses/views.py
# courses/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Course, Module, ModuleContent, 
    Assignment, AssignmentSubmission, Enrollment
)
from .serializers import (
    CourseSerializer, ModuleSerializer, ModuleContentSerializer,
    AssignmentSerializer, AssignmentSubmissionSerializer, EnrollmentSerializer
)
from .permissions import IsInstructor, IsStudent, IsAdmin

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.prefetch_related('modules').select_related('instructor')
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsInstructor()]
        elif self.action in ['my_courses', 'in_progress_courses', 'completed_courses']:
            return [IsStudent()]
        else:
            return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsInstructor])
    def my_courses(self, request):
        courses = self.queryset.filter(instructor=request.user)
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsStudent])
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

    @action(detail=False, methods=['get'], permission_classes=[IsStudent])
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
    permission_classes = [permissions.IsAuthenticated, IsInstructor | IsAdmin]
    serializer_class = ModuleSerializer

    def get_queryset(self):
        """
        Order modules by 'order' and optionally filter by course.
        """
        queryset = Module.objects.select_related('course') \
                                 .prefetch_related('contents', 'assignments') \
                                 .order_by('order')
        course_id = self.kwargs.get('course_pk')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Only enrolled users can list modules for a given course.
        """
        course_id = self.kwargs.get('course_pk')
        if course_id:
            is_enrolled = Enrollment.objects.filter(
                user=request.user,
                course_id=course_id,
                status='active'
            ).exists()
            if not is_enrolled:
                return Response(
                    {"detail": "You are not enrolled in this course."},
                    status=status.HTTP_403_FORBIDDEN
                )
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Only enrolled users can retrieve a specific module.
        """
        module = self.get_object()
        is_enrolled = Enrollment.objects.filter(
            user=request.user,
            course=module.course,
            status='active'
        ).exists()
        if not is_enrolled:
            return Response(
                {"detail": "You are not enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Ensure the module is associated with an existing course.
        """
        course_id = self.kwargs.get('course_pk')
        serializer.save(course_id=course_id)


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
        module_id = self.kwargs.get('module_pk')
        serializer.save(module_id=module_id)


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
        module_id = self.kwargs.get('module_pk')
        serializer.save(module_id=module_id)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing assignment submissions by students.
    """
    queryset = AssignmentSubmission.objects.all().select_related('assignment', 'student')
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def perform_create(self, serializer):
        """
        Allow students to submit their assignments.
        """
        assignment_id = self.kwargs.get('assignment_pk')
        serializer.save(student=self.request.user, assignment_id=assignment_id)

    @action(detail=False, methods=['get'], permission_classes=[IsStudent])
    def my_submissions(self, request):
        """
        Custom action for students to view their submissions.
        """
        submissions = self.queryset.filter(student=request.user)
        serializer = self.get_serializer(submissions, many=True)
        return Response(serializer.data)


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing enrollments.
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Create an enrollment for the user.
        """
        serializer.save(user=self.request.user)


