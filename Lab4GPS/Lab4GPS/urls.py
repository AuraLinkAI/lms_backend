# Lab4GPS/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),

    # Auths app URLs
    path('auth/', include('Auths.urls')),

    # Archive app URLs
    path('archive/', include('Archive.urls')),  

    # Courses app URLs
    path('courses/', include('courses.urls')), 

    # Menu app URLs
    path('menu/', include('menu.urls')),   
    
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
