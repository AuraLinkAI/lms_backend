from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from Auths.models import CustomUser  # Ensure this matches the correct app name


class Category(models.Model):
    """
    Model representing predefined categories for files.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    @staticmethod
    def initialize_defaults():
        """
        Create predefined categories if they do not already exist.
        """
        default_categories = ["Research Materials", "Project Documentation", "Key Achievements"]
        for category in default_categories:
            Category.objects.get_or_create(name=category)

    @classmethod
    def get_all(cls):
        """
        Ensure the defaults are initialized before fetching all categories.
        """
        cls.initialize_defaults()
        return cls.objects.all()


class Tag(models.Model):
    """
    Model representing predefined tags for files.
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    @staticmethod
    def initialize_defaults():
        """
        Create predefined tags if they do not already exist.
        """
        default_tags = ["Sustainability", "Research", "AI", "Innovation", "Achievements", "Summary"]
        for tag in default_tags:
            Tag.objects.get_or_create(name=tag)

    @classmethod
    def get_all(cls):
        """
        Ensure the defaults are initialized before fetching all tags.
        """
        cls.initialize_defaults()
        return cls.objects.all()


class File(models.Model):
    """
    Model representing a file in the archive.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="files"
    )
    tags = models.ManyToManyField(Tag, related_name="files")
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="uploaded_files"
    )
    upload_date = models.DateTimeField(default=timezone.now)
    version = models.PositiveIntegerField(default=1)
    file = models.FileField(upload_to="uploaded_files/")
    media = models.URLField(
        max_length=500, blank=True, null=True, help_text="Optional image or video URL"
    )
    external_link = models.URLField(
        max_length=500, blank=True, null=True, help_text="Optional external document link"
    )
    views = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} by {self.author.get_full_name()}"

    def clean(self):
        """
        Validation to ensure category and tags are selected.
        """
        if not self.category:
            raise ValidationError("Category is required.")
        if not self.tags.exists():
            raise ValidationError("At least one tag is required.")

    def increment_views(self):
        """
        Increment the view count for the file.
        """
        self.views += 1
        self.save()

    def increment_downloads(self):
        """
        Increment the download count for the file.
        """
        self.downloads += 1
        self.save()


class Comment(models.Model):
    """
    Model representing comments on files.
    """
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.get_full_name()} on {self.file.title}"


class Like(models.Model):
    """
    Model representing likes on files.
    """
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="likes"
    )

    class Meta:
        unique_together = ("file", "user")

    def __str__(self):
        return f"{self.user.get_full_name()} liked {self.file.title}"
