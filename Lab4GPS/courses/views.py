# courses/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import (
    Course, Module, Chapter, ChapterContent,
    Assignment, AssignmentSubmission, Enrollment, ModuleProgress,
)
from .serializers import (
    CourseSerializer, ModuleSerializer, ChapterSerializer, ChapterContentSerializer,
    AssignmentSerializer, AssignmentSubmissionSerializer, EnrollmentSerializer,
    ModuleProgressSerializer,
)
from .permissions import IsInstructorOrAdmin, IsStudent, IsAdmin


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.prefetch_related('modules').select_related('instructor')
    serializer_class = CourseSerializer

    def get_permissions(self):
        """
        Make sure instructors/admin can create/update;
        my_courses => instructor or admin,
        in_progress or completed => student,
        else => allow any.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsInstructorOrAdmin()]
        elif self.action == 'my_courses':
            return [IsInstructorOrAdmin()]
        elif self.action in ['in_progress_courses', 'completed_courses']:
            return [IsStudent()]
        else:
            return [permissions.AllowAny()]

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsInstructorOrAdmin])
    def my_courses(self, request):
        """Return only the courses created by request.user if they're instructor/admin."""
        courses = self.queryset.filter(instructor=request.user)
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsStudent])
    def in_progress_courses(self, request):
        enrollments = Enrollment.objects.filter(user=request.user, status='in-progress')
        course_ids = enrollments.values_list('course_id', flat=True)
        courses = self.queryset.filter(id__in=course_ids)
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsStudent])
    def completed_courses(self, request):
        enrollments = Enrollment.objects.filter(user=request.user, status='completed')
        course_ids = enrollments.values_list('course_id', flat=True)
        courses = self.queryset.filter(id__in=course_ids)
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)
class ModuleViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsStudent | IsInstructorOrAdmin]
    serializer_class = ModuleSerializer

    def get_queryset(self):
        print("DEBUG: Entered ModuleViewSet.get_queryset() for user:", self.request.user)
        queryset = Module.objects.select_related('course').order_by('order')
        course_id = self.kwargs.get('course_pk')

        if course_id:
            queryset = queryset.filter(course_id=course_id)

            # AUTO-ENROLL logic
            if (self.request.user.is_authenticated 
                and hasattr(self.request.user, 'profile') 
                and self.request.user.profile.role == 'student'):
                
                enrollment, created = Enrollment.objects.get_or_create(
                    user=self.request.user,
                    course_id=course_id,
                    defaults={'status': 'in-progress'}
                )
                
                if created:
                    print(
                        f"DEBUG: Created new enrollment for user={self.request.user} in course_id={course_id}"
                    )
                else:
                    print(
                        f"DEBUG: Enrollment already exists for user={self.request.user} in course_id={course_id}"
                    )

        return queryset

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def detailed_view(self, request, course_pk=None, pk=None):
        module = get_object_or_404(Module, course_id=course_pk, id=pk)
        serializer = self.get_serializer(module)
        return Response(serializer.data)


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructorOrAdmin]

    def get_queryset(self):
        # Filter by module if in nested route
        module_id = self.kwargs.get('module_pk')
        qs = super().get_queryset()
        if module_id:
            qs = qs.filter(module_id=module_id)
        return qs

    def perform_create(self, serializer):
        module_id = self.kwargs.get('module_pk')
        serializer.save(module_id=module_id)


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all().select_related('module')
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructorOrAdmin]

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

    @action(detail=True, methods=['post'], permission_classes=[IsStudent])
    def mark_completed(self, request, pk=None):
        enrollment = get_object_or_404(Enrollment, pk=pk, user=request.user)
        enrollment.status = 'completed'
        enrollment.save()
        return Response({'status': 'Course marked as completed.'}, status=status.HTTP_200_OK)


class ModuleProgressViewSet(viewsets.ModelViewSet):
    queryset = ModuleProgress.objects.all().select_related('module', 'user')

    # Ensure DRF knows which serializer to use
    serializer_class = ModuleProgressSerializer

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Admins see all progress; everyone else sees only their own.
        """
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.role == 'admin':
            return ModuleProgress.objects.all()
        return ModuleProgress.objects.filter(user=user)

    def perform_create(self, serializer):
        # Attach to current user on create
        serializer.save(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    # ---------------------------------------
    # CUSTOM PATCH: /courses/<course_pk>/modules/<module_pk>/progress/
    # This "upserts" progress if no record, otherwise updates existing
    # ---------------------------------------
    @action(
        detail=False,
        methods=['patch'],
        url_path='',
        permission_classes=[permissions.IsAuthenticated]
    )
    def patch_progress(self, request, course_pk=None, module_pk=None):
        """
        PATCH /courses/<course_pk>/modules/<module_pk>/progress/
        Body: { "progress": 0..100 }

        1) get_or_create user’s ModuleProgress record.
        2) Update with the given progress.
        3) Check if ALL modules in the course are at 100% => mark the Enrollment as completed.
        """
        progress_val = request.data.get('progress')
        if progress_val is None:
            return Response({"detail": "Missing 'progress' field"}, status=400)

        # Validate it's an integer 0 <= progress <= 100
        try:
            progress_val = int(progress_val)
        except ValueError:
            return Response({"detail": "progress must be an integer"}, status=400)

        if progress_val < 0 or progress_val > 100:
            return Response({"detail": "progress must be between 0 and 100"}, status=400)

        # Confirm the module belongs to that course
        module = get_object_or_404(Module, pk=module_pk, course__pk=course_pk)

        # Upsert the ModuleProgress
        module_progress, created = ModuleProgress.objects.get_or_create(
            user=request.user,
            module=module
        )
        module_progress.progress = progress_val
        module_progress.save()

        # ---------------------------------------------
        # Check if user now has 100% in ALL modules of this course
        # ---------------------------------------------
        total_modules = Module.objects.filter(course=module.course).count()
        completed_modules = ModuleProgress.objects.filter(
            user=request.user,
            module__course=module.course,
            progress=100
        ).count()

        if total_modules > 0 and completed_modules == total_modules:
            # Mark user’s enrollment as completed (if it exists)
            enrollment_qs = Enrollment.objects.filter(user=request.user, course=module.course)
            if enrollment_qs.exists():
                enrollment = enrollment_qs.first()
                enrollment.status = 'completed'
                enrollment.save()

        # Return updated progress
        serializer = self.get_serializer(module_progress)
        return Response(serializer.data, status=200)