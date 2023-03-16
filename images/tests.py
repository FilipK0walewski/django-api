import io

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile

from PIL import Image

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import CustomUser, Tier, Image as ImageModel


class ImageTestCase(APITestCase):

    def setUp(self):
        Tier.objects.create(name='Test', sizes=[200, 400], original_image_access=False, expiring_link_access=False)
        self.user = CustomUser.objects.create(username='test', password='123', tier=Tier.objects.all().first())
        ImageModel.objects.create(image=self.get_temp_image('jpeg'), owner=self.user)

        self.tiers = Tier.objects.all()
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
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['count'], ImageModel.objects.filter(owner=self.user).count())

    def test_image_retrive(self):
        user_images = ImageModel.objects.filter(owner=self.user)
        for img in user_images:
            for size in self.user.tier.sizes:
                response = self.client.get(f'/images/{img.id}/?size={size}')
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.client.get(f'/images/{img.id}/')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_expire_url_create(self):
        self.user.tier.expiring_link_access = True
        first_image = ImageModel.objects.filter(owner=self.user).first()
        
        response = self.client.post('/expiring-link/', {'image_id': first_image.id, 'seconds': 300})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post('/expiring-link/', {'image_id': first_image.id, 'seconds': 30000})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post('/expiring-link/', {'image_id': first_image.id, 'seconds': 299})
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        response = self.client.post('/expiring-link/', {'image_id': first_image.id, 'seconds': 30001})
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_jpg_create(self):
        response = self.client.post('/images/', {'image': self.get_temp_image('JPEG')}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_png_create(self):
        response = self.client.post('/images/', {'image': self.get_temp_image('PNG')}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_webp_create(self):
        response = self.client.post('/images/', {'image': self.get_temp_image('WEBP')}, follow=True)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_empty_create(self):
        response = self.client.post('/images/', follow=True)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
