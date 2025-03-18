# wishlist/serializers.py
from rest_framework import serializers
from .models import Wishlist
from courses.models import Course
from .models import Notification, HelpTopic, UserSetting

# Simple serializer for the course fields you want to show
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "description", "cover_image"]

# Wishlist serializer
class WishlistSerializer(serializers.ModelSerializer):
    # Read-only nested course object
    course = CourseSerializer(read_only=True)
    # Write-only course_id field to create the relationship
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source="course", write_only=True
    )

    class Meta:
        model = Wishlist
        fields = ["id", "course", "course_id", "added_at"]



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at', 'is_read']

class HelpTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpTopic
        fields = ['id', 'title', 'content']

class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = ['theme', 'notifications', 'language']
