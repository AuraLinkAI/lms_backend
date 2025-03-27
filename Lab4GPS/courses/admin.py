# courses/admin.py
from django.contrib import admin
from .models import (
    Course, Module, Chapter, ChapterContent,
    Assignment, AssignmentSubmission
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'instructor__username')
    list_filter = ('instructor', 'created_at')
    ordering = ('-created_at',)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    search_fields = ('title', 'course__title')
    list_filter = ('course',)
    ordering = ('course', 'order')


##########################################################
# Register new Chapter and ChapterContent
##########################################################
@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order')
    search_fields = ('title', 'module__title')
    list_filter = ('module',)
    ordering = ('module', 'order')


@admin.register(ChapterContent)
class ChapterContentAdmin(admin.ModelAdmin):
    list_display = ('content_title', 'content_type', 'chapter', 'created_at')
    search_fields = ('content_title', 'chapter__title')
    list_filter = ('content_type', 'chapter', 'created_at')
    ordering = ('-created_at',)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'due_date', 'max_score')
    search_fields = ('title', 'module__title')
    list_filter = ('module', 'due_date')
    ordering = ('due_date',)


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'grade')
    search_fields = ('assignment__title', 'student__username')
    list_filter = ('assignment', 'grade', 'submitted_at')
    ordering = ('-submitted_at',)
