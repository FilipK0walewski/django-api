from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from images.views import ExpiringLinkViewSet, ImageViewSet

router = DefaultRouter()
router.register(r'expiring-link', ExpiringLinkViewSet, basename='expiringlinkviewset')
router.register(r'images', ImageViewSet, basename='image')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
