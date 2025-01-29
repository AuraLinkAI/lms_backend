from django.contrib import admin
from .models import Category, Tag, File, Comment, Like


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Category model.
    """
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin interface for Tag model.
    """
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    """
    Admin interface for File model.
    """
    list_display = ('id', 'title', 'author', 'category', 'upload_date', 'downloads', 'views')
    list_filter = ('category', 'tags', 'upload_date')
    search_fields = ('title', 'description', 'author__username')
    readonly_fields = ('views', 'downloads')
    filter_horizontal = ('tags',)
    fieldsets = (
        ("Basic Information", {
            'fields': ('title', 'description', 'category', 'tags', 'author', 'version')
        }),
        ("Media and Links", {
            'fields': ('file', 'media', 'external_link')
        }),
        ("Statistics", {
            'fields': ('views', 'downloads')
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for Comment model.
    """
    list_display = ('id', 'file', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('file__title', 'user__username', 'text')
    date_hierarchy = 'created_at'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """
    Admin interface for Like model.
    """
    list_display = ('id', 'file', 'user')
    search_fields = ('file__title', 'user__username')
    list_filter = ('file',)
