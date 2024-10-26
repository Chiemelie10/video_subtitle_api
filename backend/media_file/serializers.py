"""This module defines class MediaFileSerializer and FileChunkSerializer."""
from rest_framework import serializers
from .models import FileChunk, MediaFile


class FileChunkSerializer(serializers.ModelSerializer):
    """This class validates and serializes the FileChunk model."""
    class Meta:
        """
            model: Name of the model
            fields: The class attributes of the above name model
                    to be validated
        """
        model = FileChunk
        fields = [
            'id',
            'media_file',
            'media_type', 
            'chunk',
            'chunk_number',
            'chunk_size',
            'file_name',
            'total_size'
        ]

    def validate(self, attrs):
        """
        This method validates the request and returns the value of the attrs in the request.
        """
        # pylint: disable=no-member

        chunk = attrs.get('chunk')
        media_file = attrs.get('media_file')
        media_type = attrs.get('media_type')
        req_chunk_number = attrs.get('chunk_number')
        req_chunk_size = attrs.get('chunk_size')
        req_total_size = attrs.get('total_size')
        req_file_name = attrs.get('file_name')

        chunk_size = chunk.size
        if req_chunk_size != chunk_size:
            raise serializers.ValidationError(
                f'Chunk size mismatch. File size is {chunk_size} bytes, sent {req_chunk_size} bytes.'
            )
    
        if req_chunk_number > 1 and media_file is None:
            raise serializers.ValidationError(
                'Media file id is required when chunk number is greater than 1.'
            )

        if media_file:
            chunks = media_file.chunks.all()
            current_total_size = chunk_size

            num_of_chunks = len(chunks)
            if (num_of_chunks + 1) != req_chunk_number:
                raise serializers.ValidationError(
                    f'Chunk number mismatch. Chunk number should be {num_of_chunks}, '
                    f'sent {req_chunk_number}.'
                )

            for chunk in chunks:
                if media_type != chunk.media_type:
                    raise serializers.ValidationError('Media type mismatch.')
                if req_file_name != chunk.file_name:
                    raise serializers.ValidationError('File name mismatch.')
                if media_type != chunk.media_type:
                    raise serializers.ValidationError('Media type mismatch.')
                current_total_size += chunk.chunk_size

            if current_total_size == req_total_size:
                attrs['is_last_chunk'] = True
            elif current_total_size > req_total_size:
                # Perform deletion logic
                raise serializers.ValidationError('Total size exceeded.')
        else:
            if chunk_size == req_total_size:
                attrs['is_last_chunk'] = True
            elif chunk_size > req_total_size:
                # Perform deletion logic
                raise serializers.ValidationError('Total size exceeded.')

            new_media_file = MediaFile.objects.create(media_type=media_type, file_name=req_file_name)
            attrs['media_file'] = new_media_file

        return attrs

    def validate_chunk(self, chunk):
        """Does extra validation on chunk field."""
        if chunk.size > 1024 * 1024 * 5:
            raise serializers.ValidationError('Chunk size exceeds 5 mb.')

        return chunk


class MediaFileSerializer(serializers.ModelSerializer):
    """This class validates and serializes the FileChunk model."""
    file = serializers.FileField(required=True)

    class Meta:
        """
            model: Name of the model
            fields: The class attributes of the above name model
                    to be validated
        """
        model = MediaFile
        fields = [
            'id',
            'file',
            'media_type',
            'file_size',
            'file_name'
        ]

    def validate(self, attrs):
        """
        This method validates the request and returns the value of the attrs in the request.
        """
        file = attrs.get('file')
        attrs['file_size'] = file.size
        return attrs

    def validate_file(self, file):
        """Does extra validation on file field."""
        if file.size > 1024 * 1024 * 5:
            raise serializers.ValidationError('File size exceeds 5 mb.')

        allowed_mimetypes = ['video/mp4', 'audio/mp3']
        if file.content_type not in allowed_mimetypes:
            raise serializers.ValidationError('File mimetype not allowed.')

        return file
