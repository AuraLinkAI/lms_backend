from rest_framework import serializers
from .models import Category, Tag, File, Comment, Like
from Auths.models import CustomUser  # Ensure this matches the correct app name


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    """
    class Meta:
        model = Category
        fields = ['id', 'name']


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag model.
    """
    class Meta:
        model = Tag
        fields = ['id', 'name']


class FileSerializer(serializers.ModelSerializer):
    """
    Serializer for File model, including nested relationships.
    """
    category = serializers.SlugRelatedField(
        slug_field='name', queryset=Category.objects.all()
    )  # Allows setting category by name
    tags = serializers.SlugRelatedField(
        slug_field='name', queryset=Tag.objects.all(), many=True
    )  # Allows setting tags by name
    author = serializers.SerializerMethodField()  # Display author's full name
    likes_count = serializers.SerializerMethodField()  # Number of likes
    comments_count = serializers.SerializerMethodField()  # Number of comments
    file_url = serializers.SerializerMethodField()  # URL for the file
    is_liked = serializers.SerializerMethodField()  # Whether the current user has liked the file

    downloads_count = serializers.IntegerField(source='downloads', read_only=True)  # Track downloads count

    class Meta:
        model = File
        fields = [
            'id', 'title', 'description', 'category', 'tags', 'author',
            'upload_date', 'version', 'file', 'media', 'external_link',
            'views', 'downloads_count', 'likes_count', 'comments_count', 'file_url', 'is_liked'
        ]

    def get_author(self, obj):
        """
        Returns the full name of the author.
        """
        return obj.author.get_full_name() if obj.author else None

    def get_likes_count(self, obj):
        """
        Returns the total number of likes for the file.
        """
        return obj.likes.count()

    def get_comments_count(self, obj):
        """
        Returns the total number of comments for the file.
        """
        return obj.comments.count()

    def get_file_url(self, obj):
        """
        Returns the full URL for the uploaded file.
        """
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

    def get_is_liked(self, obj):
        """
        Checks if the current user has liked the file.
        """
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.likes.filter(user=user).exists()
        return False


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    """
    user = serializers.SerializerMethodField()  # Display user's full name
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')  # Format date

    class Meta:
        model = Comment
        fields = ['id', 'file', 'user', 'text', 'created_at']

    def get_user(self, obj):
        """
        Returns the full name of the user who made the comment.
        """
        return obj.user.get_full_name() if obj.user else None


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for Like model.
    """
    user = serializers.SerializerMethodField()  # Display user's full name

    class Meta:
        model = Like
        fields = ['id', 'file', 'user']

    def get_user(self, obj):
        """
        Returns the full name of the user who liked the file.
        """
        return obj.user.get_full_name() if obj.user else None
