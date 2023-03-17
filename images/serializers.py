import os
import uuid

from PIL import Image

from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from .models import CustomUser, ExpiringLink, Image as ImageModel


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id',)


class ImageSerializer(serializers.Serializer):

    image = serializers.ImageField(write_only=True)
    image_name = serializers.SerializerMethodField(read_only=True)
    urls = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ImageModel
        fields = ('id', 'image', 'image_name', 'urls')

    def get_image_name(self, obj):
        return obj.image.path.split('/')[-1]

    def get_urls(self, obj):
        urls = {}
        img_url = f'/images/{obj.id}'
        for size in obj.owner.tier.sizes:
            urls[f'{size}px'] = f'{img_url}?size={size}'

        if obj.owner.tier.original_image_access is True:
            urls['original_size'] = img_url

        return urls

    def create(self, validated_data):
        return ImageModel.objects.create(image=validated_data['image'], owner=validated_data['user'])

    def is_valid(self):
        if super().is_valid() is not True:
            return False

        img = Image.open(self.validated_data['image'])
        if img.format not in ['JPEG', 'PNG']:
            return False
        return True


class ExpiringLinkSerializer(serializers.Serializer):
    
    image_id = serializers.IntegerField(write_only=True)
    image = ImageSerializer(read_only=True)
    seconds = serializers.IntegerField(write_only=True, min_value=300, max_value=30000)
    uuid = serializers.UUIDField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        expires_at = timezone.now() + timedelta(seconds=validated_data['seconds'])
        image = ImageModel.objects.get(id=validated_data['image_id'])
        return ExpiringLink.objects.create(image=image, expires_at=expires_at, uuid=uuid.uuid4())

    def is_valid(self):
        if super().is_valid() is not True:
            return False
        
        seconds = self.validated_data['seconds']
        if not(30000 >= seconds >= 300):
            return False
        return str(seconds).isdigit()
