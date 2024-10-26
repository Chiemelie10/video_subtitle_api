"""This module defines the routes of media_file app."""
from django.urls import path
from .views import MediaFileView, FileChunkView


urlpatterns = [
    path('api/uploads/chunks', FileChunkView.as_view(), name='upload-chunk-file'),
    path('api/uploads/media', MediaFileView.as_view(), name='upload-media-file'),
]
