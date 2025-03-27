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
    order = models.PositiveIntegerField(default=0)  # order of modules in the course

    def __str__(self):
        return f"{self.title} - {self.course.title}"

##########################################################
# NEW: Chapter & ChapterContent, nested under Module
##########################################################
class Chapter(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)  # order of chapters in the module

    def __str__(self):
        return f"{self.title} (Module: {self.module.title})"


class ChapterContent(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='contents')

    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('text', 'Text'),
        ('document', 'Document'),
        ('image', 'Image'),
        ('presentation', 'Presentation'),
    ]
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES)
    content_title = models.CharField(max_length=255)
    text = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='chapter_contents/', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content_type}: {self.content_title} (Ch: {self.chapter.title})"


class Assignment(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to='assignments/', null=True, blank=True)
    max_score = models.PositiveIntegerField(default=100)

    def __str__(self):
        return f"{self.title} - {self.module.title}"


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/', null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignment.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='in-progress')

    def __str__(self):
        return f'{self.user.username} enrolled in {self.course.title}'


class ModuleProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='module_progresses')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='progresses')
    progress = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'module')
        verbose_name = 'Module Progress'
        verbose_name_plural = 'Module Progresses'

    def __str__(self):
        return f"{self.user.username} - {self.module.title} - {self.progress}%"
