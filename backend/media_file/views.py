"""This module defines class MediaFileView and FileChunkView."""
import os
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .serializers import MediaFileSerializer, FileChunkSerializer
from .models import MediaFile, FileChunk


class MediaFileView(APIView):
    """This class define a method for uploading a file"""
    serializer_class = MediaFileSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        """This method saves a media file to the database."""
        # pylint: disable=no-member

        serializer = MediaFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        file = validated_data.get('file')
        file_size = validated_data.get('file_size')
        media_type = validated_data.get('media_type')
        file_name = validated_data.get('file_name')

        if file and file_name is None:
            file_name = file.name

        file = MediaFile.objects.create(
            file=file,
            file_size=file_size,
            media_type=media_type,
            file_name=file_name
        )

        serializer = MediaFileSerializer(file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FileChunkView(APIView):
    """This class defines a method for uploading a file in chunks"""
    # pylint: disable=no-member

    serializer_class = FileChunkSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        """This method saves a media file to the database."""
        serializer = FileChunkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        file_chunk = validated_data.get('chunk')
        file_size = validated_data.get('file_size')
        media_type = validated_data.get('media_type')
        media_file = validated_data.get('media_file')
        chunk_number = validated_data.get('chunk_number')
        chunk_size = validated_data.get('chunk_size')
        total_size = validated_data.get('total_size')
        file_name = validated_data.get('file_name')
        is_last_chunk = validated_data.get('is_last_chunk')

        # Create a directory for storing chunks for the media file (if not already present)
        chunk_media_directory = os.path.join(settings.MEDIA_ROOT, 'chunks')
        os.makedirs(chunk_media_directory, exist_ok=True)

        chunk_file_name = f'{media_file}_{chunk_number}'
        chunk_file_path = os.path.join(chunk_media_directory, chunk_file_name)

        with open(chunk_file_path, 'wb+') as destination:
            for chunk in file_chunk.chunks():
                destination.write(chunk)

        file = FileChunk.objects.create(
            chunk_file_path=chunk_file_path,
            file_size=file_size,
            media_type=media_type,
            chunk_number=chunk_number,
            chunk_size=chunk_size,
            total_size=total_size,
            file_name=file_name,
            is_last_chunk=is_last_chunk
        )

        if is_last_chunk is False:
            response_data = {
                'media_file_id': media_file,
                'next_chunk_number': chunk_number + 1
            }
            return Response(response_data, status=status.HTTP_200_OK)

        chunks = FileChunk.objects.filter(media_file=media_file).order_by('chunk_number')
        empty_media_file = MediaFile.objects.get(id=media_file)
        empty_media_file_name = empty_media_file.file_name

        media_directory = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(media_directory, exist_ok=True)

        media_file_path = os.path.join(media_directory, empty_media_file_name)

        with open(media_file_path, 'wb') as media_file_destination:
            for chunk in chunks:
                with open(chunk.chunk_file_path, 'rb') as chunk_file:
                    media_file_destination.write(chunk_file.read())

        empty_media_file.file.name = f'uploads/{empty_media_file_name}'
        empty_media_file.save()

        serializer = MediaFileSerializer(file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
