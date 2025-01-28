# models.py
from django.db import models
from django.conf import settings  # Import settings to access the custom user model

# Stamp Model
class Stamp(models.Model):
    SHAPE_CHOICES = [
        ('Circle', 'Circle'),
        ('Square', 'Square'),
        ('Star', 'Star'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stamps")
    shape = models.CharField(max_length=20, choices=SHAPE_CHOICES)
    shape_color = models.CharField(max_length=7)  # HEX color
    text_color = models.CharField(max_length=7)  # HEX color
    date_color = models.CharField(max_length=7)  # HEX color
    date = models.DateField()
    top_text = models.CharField(max_length=100)
    bottom_text = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shape} Stamp - {self.user.username}"


# Document Model
class Document(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(upload_to="documents/")
    metadata = models.JSONField(default=dict)  # Store metadata like timestamp, user ID
    stamped = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)  # Add a timestamp field
    version = models.CharField(max_length=100, default="1.0")  # Add a version field

    def __str__(self):
        return f"Document by {self.user.username}"
