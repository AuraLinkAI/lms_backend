from rest_framework import serializers
from .models import Course, Module, ModuleContent, Assignment, AssignmentSubmission, Enrollment


class ModuleContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleContent
        fields = ['id', 'content_type', 'content_title', 'text', 'file', 'video_url', 'created_at']


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'due_date', 'file', 'max_score']


class ModuleSerializer(serializers.ModelSerializer):
    contents = ModuleContentSerializer(many=True, read_only=True)
    assignments = AssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order', 'contents', 'assignments']


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'cover_image', 'instructor', 'modules', 'created_at']
        read_only_fields = ['instructor', 'created_at']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'student', 'file', 'text', 'submitted_at', 'grade']


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'user', 'enrolled_at', 'status']
        read_only_fields = ['user', 'enrolled_at']  # status should be writable if it needs to be set during POST

    def create(self, validated_data):
        # Custom creation logic here, if needed
        return super().create(validated_data)
