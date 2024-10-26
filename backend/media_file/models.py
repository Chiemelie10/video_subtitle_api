"""This module defines class MediaFile"""
from uuid import uuid4
from django.db import models
# from django.contrib.auth import get_user_model


# User = get_user_model()

MEDIA_TYPE_CHIOCES=(
    ('Video', 'Video'),
    ('Audio', 'Audio')
)

class MediaFile(models.Model):
    """This class defines the attributes of the Files class."""
    id = models.CharField(default=uuid4, max_length=36, primary_key=True,
                          editable=False, unique=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHIOCES)
    file_size = models.IntegerField(default=0)
    file_name = models.CharField(max_length=1000, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """ db_table: Name of the table this class creates in the database."""
        db_table = 'media_files'
        ordering = ['-uploaded_at']

    def __str__(self):
        """This method returns a string representation of the instance of this class."""
        # pylint: disable=no-member
        return f'{self.media_type} - {self.file.name}'


class FileChunk(models.Model):
    """This class defines the attributes of the Files class."""
    id = models.CharField(default=uuid4, max_length=36, primary_key=True,
                          editable=False, unique=True)
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE,
                                   related_name='chunks', db_index=True, null=True)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHIOCES)
    chunk_file_path = models.CharField(max_length=500, blank=True, null=True)
    chunk_number = models.PositiveIntegerField()
    chunk_size = models.PositiveIntegerField(default=5242880) # 5 MB per chunk
    total_size = models.PositiveIntegerField()
    file_name = models.CharField(max_length=1000)
    is_last_chunk = models.BooleanField(default=False)

    class Meta:
        """ db_table: Name of the table this class creates in the database."""
        unique_together = ('media_file', 'chunk_number')
        ordering = ['chunk_number']
