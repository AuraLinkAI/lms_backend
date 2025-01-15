# courses/models.py
from django.db import models
from django.conf import settings

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='course_covers/', null=True, blank=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Module(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    order = models.PositiveIntegerField(default=0)  # To maintain module order

    def __str__(self):
        return f"{self.title} - {self.course.title}"


class ModuleContent(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='contents')
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('text', 'Text'),
        ('document', 'Document'),
        ('image', 'Image'),
        ('presentation', 'Presentation'),
    ]
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES)
    content_title = models.CharField(max_length=255)
    text = models.TextField(null=True, blank=True)  # For text content
    file = models.FileField(upload_to='module_contents/', null=True, blank=True)  # For files
    video_url = models.URLField(null=True, blank=True)  # For video links
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content_type}: {self.content_title}"


class Assignment(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to='assignments/', null=True, blank=True)  # Assignment resources
    max_score = models.PositiveIntegerField(default=100)

    def __str__(self):
        return f"{self.title} - {self.module.title}"


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/', null=True, blank=True)  # Submitted file
    text = models.TextField(null=True, blank=True)  # Submitted text
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.PositiveIntegerField(null=True, blank=True)  # Graded score

    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignment.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='active')

    def __str__(self):
        return f'{self.user.username} enrolled in {self.course.title}'


class ModuleProgress(models.Model):
    """
    Model to track user progress for each module.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='module_progresses')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='progresses')
    progress = models.PositiveIntegerField(default=0)  # Progress percentage (0-100)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'module')
        verbose_name = 'Module Progress'
        verbose_name_plural = 'Module Progresses'

    def __str__(self):
        return f"{self.user.username} - {self.module.title} - {self.progress}%"
