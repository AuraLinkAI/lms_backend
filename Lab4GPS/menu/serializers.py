from rest_framework import serializers
from .models import Wishlist
from courses.models import Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "description", "cover_image"]

class WishlistSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source="course", write_only=True
    )

    class Meta:
        model = Wishlist
        fields = ["id", "course", "course_id", "added_at"]
