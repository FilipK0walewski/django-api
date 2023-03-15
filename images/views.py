import io
import os

from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from PIL import Image

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet

from .models import ExpiringLink, Image as ImageModel
from .serializers import ExpiringLinkSerializer, ImageSerializer


class ImageViewSet(ModelViewSet):

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ImageSerializer

    def get_queryset(self):
        return ImageModel.objects.filter(owner=self.request.user).order_by('id')

    def list(self, request):
        if request.user.tier is None:
            return Response({'message': 'User has no tier.'}, status=status.HTTP_403_FORBIDDEN)
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk):
        size = request.query_params.get('size')
        if size is not None and size.isnumeric() is False:
            return Response({'message': 'Invalid size.'}, status=status.HTTP_400_BAD_REQUEST)

        if size is not None:
            size = int(size)

        image = self.get_object()
        image_path = image.image.path

        if image.owner.id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if os.path.exists(image_path) is False:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if size is None and request.user.tier.original_image_access is False:
            return Response(status=status.HTTP_403_FORBIDDEN)
        elif size is not None and size not in request.user.tier.sizes:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if size is None:
            return FileResponse(open(image_path, 'rb'))

        img_bytes = io.BytesIO()
        img = Image.open(image_path)
        img_format = img.format
        width, height = img.size
        scale = height / size

        img.thumbnail((width // scale, size))
        img.save(img_bytes, img_format)
        response = HttpResponse(content_type=f'image/{img_format.lower()}')
        response.write(img_bytes.getvalue())
        return response

    def create(self, request):
        if request.user.tier is None:
            return Response({'message': 'User has no tier.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            return Response({'message': 'Invalid image.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user)
        return Response(serializer.data)


class ExpiringLinkViewSet(ViewSet):

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ExpiringLinkSerializer

    def retrieve(self, request, pk):
        permission_classes = None
        link = get_object_or_404(ExpiringLink, uuid=pk)

        if timezone.now() > link.expires_at:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = ExpiringLinkSerializer(link, many=False)
        return FileResponse(open(serializer.data['image']['image_path'], 'rb'))

    def create(self, request):
        if request.user.tier is None:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if request.user.tier.expiring_link_access is False:
            return Response(status=status.HTTP_403_FORBIDDEN)

        img = get_object_or_404(ImageModel, id=request.data['image_id'])
        if img.owner.id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = ExpiringLinkSerializer(data=request.data)
        if serializer.is_valid() is False:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        expiring_link = f'{settings.HOSTNAME}/expiring-link/{serializer.data["uuid"]}'
        return Response({'link': expiring_link})
