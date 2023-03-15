import io
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile

from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse

from .models import CustomUser, Tier, Image as ImageModel


class ImageTestCase(APITestCase):

    def setUp(self):
        Tier.objects.create(name='Basic', sizes=[200], original_image_access=False, expiring_link_access=False)
        Tier.objects.create(name='Premium', sizes=[200,400], original_image_access=True, expiring_link_access=False)
        Tier.objects.create(name='Enterpise', sizes=[200,400], original_image_access=True, expiring_link_access=True)
        self.tiers = Tier.objects.all()
        self.user = CustomUser.objects.create(username='test', password='123', tier=Tier.objects.all().first())
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @staticmethod
    def get_temp_image(ext):
        img_bytes = io.BytesIO()
        img = Image.new('RGB', (100, 100))
        img.save(img_bytes, ext)
        return SimpleUploadedFile(f'test.{ext}', img_bytes.getvalue())

    def test_image_list(self):
        response = self.client.get('/images/', format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], ImageModel.objects.filter(owner=self.user).count())

    def test_jpg_create(self):
        response = self.client.post('/images/', {'image': self.get_temp_image('JPEG')}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_png_create(self):
        response = self.client.post('/images/', {'image': self.get_temp_image('PNG')}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_jpg_create(self):
        response = self.client.post('/images/', {'image': self.get_temp_image('WEBP')}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_create(self):
        response = self.client.post('/images/', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
