from django.urls import path
from .views import (
    CategoryListView,
    TagListView,
    FileListView,
    FileDetailView,
    FileUploadView,
    LikeView,
    CommentView,
    FileDownloadView,
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    
    # Tags
    path('tags/', TagListView.as_view(), name='tag-list'),
    
    # Files
    path('files/', FileListView.as_view(), name='file-list'),
    path('files/<int:pk>/', FileDetailView.as_view(), name='file-detail'),
    path('files/<int:pk>/download/', FileDownloadView.as_view(), name='file-download'),
    path('files/upload/', FileUploadView.as_view(), name='file-upload'),
    
    # Likes
    path('files/<int:pk>/like/', LikeView.as_view(), name='file-like'),
    
    # Comments
    path('files/<int:pk>/comments/', CommentView.as_view(), name='file-comments'),
]
