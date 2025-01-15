# courses/serializers.py
from rest_framework import serializers
from .models import (
    Course, Module, ModuleContent, 
    Assignment, AssignmentSubmission, Enrollment, ModuleProgress
)

class ModuleContentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        max_length=None, use_url=True, allow_null=True, required=False
    )
    
    class Meta:
        model = ModuleContent
        fields = [
            'id', 'content_type', 'content_title',
            'text', 'file', 'video_url', 'created_at'
        ]
        read_only_fields = ['module', 'created_at']

    def validate(self, data):
        content_type = data.get('content_type')
        if content_type == 'text' and not data.get('text'):
            raise serializers.ValidationError("Text content requires 'text' field.")
        if content_type == 'video' and not data.get('video_url'):
            raise serializers.ValidationError("Video content requires 'video_url' field.")
        if content_type in ['document', 'image', 'presentation'] and not data.get('file'):
            raise serializers.ValidationError(f"{content_type.capitalize()} content requires a 'file' field.")
        return data


class AssignmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        max_length=None, use_url=True, allow_null=True, required=False
    )
    
    class Meta:
        model = Assignment
        fields = ['id', 'module', 'title', 'description', 'due_date', 'file', 'max_score']


class ModuleSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True, allow_blank=False)
    description = serializers.CharField(required=True, allow_blank=False)

    contents = ModuleContentSerializer(many=True, required=False)
    assignments = AssignmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 'order', 'contents', 
            'assignments', 'course'
        ]
        read_only_fields = ['order', 'course']  # Prevent changes to the course once created

    def create(self, validated_data):
        contents_data = validated_data.pop('contents', [])
        module = Module.objects.create(**validated_data)
        for content_data in contents_data:
            ModuleContent.objects.create(module=module, **content_data)
        return module

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, required=False)  # Make writable
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'cover_image',
            'instructor', 'modules', 'created_at'
        ]
        read_only_fields = ['instructor', 'created_at']

    def create(self, validated_data):
        modules_data = validated_data.pop('modules', [])
        course = Course.objects.create(**validated_data)
        for index, module_data in enumerate(modules_data):
            # Assign 'order' based on the sequence of modules
            Module.objects.create(course=course, order=index, **module_data)
        return course


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        max_length=None, use_url=True, allow_null=True, required=False
    )
    
    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'assignment', 'student', 'file',
            'text', 'submitted_at', 'grade'
        ]
        extra_kwargs = {'student': {'read_only': True}}

    def create(self, validated_data):
        return AssignmentSubmission.objects.create(**validated_data)


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'user', 'enrolled_at', 'status']
        read_only_fields = ['user', 'enrolled_at', 'status']  # Assuming status is managed elsewhere

    def create(self, validated_data):
        # Ensure only one active enrollment per course per user
        user = self.context['request'].user
        course = validated_data['course']
        enrollment, created = Enrollment.objects.get_or_create(
            user=user, course=course, defaults={'status': 'active'}
        )
        return enrollment


class ModuleProgressSerializer(serializers.ModelSerializer):
    module = serializers.PrimaryKeyRelatedField(queryset=Module.objects.all())
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ModuleProgress
        fields = ['id', 'user', 'module', 'progress', 'last_updated']
        read_only_fields = ['user', 'last_updated']

    def validate_progress(self, value):
        if not (0 <= value <= 100):
            raise serializers.ValidationError("Progress must be between 0 and 100.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        module = validated_data['module']
        progress, created = ModuleProgress.objects.get_or_create(user=user, module=module)
        progress.progress = validated_data.get('progress', progress.progress)
        progress.save()
        return progress

    def update(self, instance, validated_data):
        instance.progress = validated_data.get('progress', instance.progress)
        instance.save()
        return instance
