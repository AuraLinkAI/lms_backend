# courses/serializers.py
from rest_framework import serializers
import json
from .models import (
    Course, Module, Chapter, ChapterContent,
    Assignment, AssignmentSubmission, Enrollment, ModuleProgress
)

class ChapterContentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        max_length=None,
        use_url=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = ChapterContent
        fields = ['id', 'content_type', 'content_title',
                  'text', 'file', 'video_url', 'created_at']
        read_only_fields = ['chapter', 'created_at']

    def validate(self, data):
        ctype = data.get('content_type')
        if ctype == 'text' and not data.get('text'):
            raise serializers.ValidationError("Text content requires 'text' field.")
        if ctype == 'video':
            # They can either provide a video_url or upload a file
            file_obj = data.get('file')
            video_url = data.get('video_url')
            if not file_obj and not video_url:
                raise serializers.ValidationError("Video content requires either 'video_url' or 'file'.")
        if ctype in ['document','image','presentation'] and not data.get('file'):
            raise serializers.ValidationError(f"{ctype.capitalize()} content requires a file.")
        return data


class ChapterSerializer(serializers.ModelSerializer):
    contents = ChapterContentSerializer(many=True, required=False)

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order', 'contents']

    def create(self, validated_data):
        contents_data = validated_data.pop('contents', [])
        chapter = Chapter.objects.create(**validated_data)
        for content_data in contents_data:
            ChapterContent.objects.create(chapter=chapter, **content_data)
        return chapter


class AssignmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        max_length=None, 
        use_url=True, 
        allow_null=True, 
        required=False
    )

    class Meta:
        model = Assignment
        fields = ['id', 'module', 'title', 'description', 'due_date', 'file', 'max_score']


class ModuleSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, required=False)

    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order', 'chapters', 'course']
        read_only_fields = ['order', 'course']

    def create(self, validated_data):
        chapters_data = validated_data.pop('chapters', [])
        module = Module.objects.create(**validated_data)
        for index, ch_data in enumerate(chapters_data):
            contents_data = ch_data.pop('contents', [])
            ch = Chapter.objects.create(module=module, order=index, **ch_data)
            for c_data in contents_data:
                ChapterContent.objects.create(chapter=ch, **c_data)
        return module


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, required=False)
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'cover_image',
            'instructor', 'modules', 'created_at', 'is_enrolled',
        ]
        read_only_fields = ['instructor', 'created_at', 'is_enrolled']

    def get_is_enrolled(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return Enrollment.objects.filter(user=user, course=obj).exists()

    def create(self, validated_data):
        request = self.context.get('request')
        modules_data_str = request.data.get('modules', None)
        if modules_data_str:
            try:
                modules_data = json.loads(modules_data_str)
            except json.JSONDecodeError:
                raise serializers.ValidationError({"modules": "Invalid JSON format."})
        else:
            modules_data = []

        course = Course.objects.create(**validated_data)

        # Create modules in the order
        for index, mod_data in enumerate(modules_data):
            chapters_data = mod_data.pop('chapters', [])
            module = Module.objects.create(course=course, order=index, **mod_data)
            for ch_index, ch_data in enumerate(chapters_data):
                contents_data = ch_data.pop('contents', [])
                chapter = Chapter.objects.create(module=module, order=ch_index, **ch_data)
                for cnt_data in contents_data:
                    file_field_key = cnt_data.get('fileFieldKey')
                    uploaded_file = None
                    if file_field_key and file_field_key in request.FILES:
                        uploaded_file = request.FILES[file_field_key]

                    ChapterContent.objects.create(
                        chapter=chapter,
                        content_type=cnt_data.get('content_type'),
                        content_title=cnt_data.get('content_title'),
                        text=cnt_data.get('text',''),
                        file=uploaded_file,
                        video_url=cnt_data.get('video_url') or cnt_data.get('link',''),
                    )

        return course


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        max_length=None, 
        use_url=True, 
        allow_null=True, 
        required=False
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
        read_only_fields = ['user', 'enrolled_at', 'status']

    def create(self, validated_data):
        user = self.context['request'].user
        course = validated_data['course']
        enrollment, created = Enrollment.objects.get_or_create(
            user=user,
            course=course,
            defaults={'status': 'in-progress'}
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
        progress, created = ModuleProgress.objects.get_or_create(
            user=user, module=module
        )
        progress.progress = validated_data.get('progress', progress.progress)
        progress.save()
        return progress

    def update(self, instance, validated_data):
        instance.progress = validated_data.get('progress', instance.progress)
        instance.save()
        return instance
