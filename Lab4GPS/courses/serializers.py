from rest_framework import serializers
from .models import Course, Module, ModuleContent, Assignment, AssignmentSubmission, Enrollment

class ModuleContentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(max_length=None, use_url=True, allow_null=True, required=False)
    
    class Meta:
        model = ModuleContent
        fields = ['id', 'module', 'content_type', 'content_title', 'text', 'file', 'video_url', 'created_at']

class AssignmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(max_length=None, use_url=True, allow_null=True, required=False)
    
    class Meta:
        model = Assignment
        fields = ['id', 'module', 'title', 'description', 'due_date', 'file', 'max_score']

class ModuleSerializer(serializers.ModelSerializer):
    contents = ModuleContentSerializer(many=True, read_only=True)
    assignments = AssignmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Module
        fields = ['id', 'course', 'title', 'description', 'order', 'contents', 'assignments']

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'cover_image', 'instructor', 'modules', 'created_at']
        read_only_fields = ['instructor', 'created_at']

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    file = serializers.FileField(max_length=None, use_url=True, allow_null=True, required=False)
    
    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'student', 'file', 'text', 'submitted_at', 'grade']
        extra_kwargs = {'student': {'read_only': True}}

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'user', 'enrolled_at', 'status']
        read_only_fields = ['user', 'enrolled_at', 'status']  # Assuming you might want to control status changes via another method or action

    def create(self, validated_data):
        # Ensure only one active enrollment per course per user
        user = self.context['request'].user
        course = validated_data['course']
        enrollment, created = Enrollment.objects.get_or_create(user=user, course=course, defaults={'status': 'active'})
        return enrollment
