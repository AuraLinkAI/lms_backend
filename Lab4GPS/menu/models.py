# wishlist/models.py
from django.db import models
from django.conf import settings
from courses.models import Course  # Import the Course model

class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist'
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='wishlisted_by'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
# menu/models.py (example new app or put in wishlist/models.py if you prefer)


class Notification(models.Model):
    """
    Stores user notifications, e.g. for system messages, updates.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:20]}"

class HelpTopic(models.Model):
    """
    Stores help topics. Could be system-wide, so no user FK required (or add one if needed).
    """
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.title

class UserSetting(models.Model):
    """
    Example user settings model if you want to store them in DB, not dummy JSON.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='setting'
    )
    theme = models.CharField(max_length=50, default='light')         # e.g. 'light' or 'dark'
    notifications = models.BooleanField(default=True)               # e.g. for enabling push/emails
    language = models.CharField(max_length=10, default='en')         # e.g. 'en', 'es', etc.

    def __str__(self):
        return f"{self.user.username} - Settings"
