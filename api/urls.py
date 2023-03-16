from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from images.views import ExpiringLinkViewSet, ImageViewSet

router = DefaultRouter()
router.register(r'images', ImageViewSet, basename='image')
router.register(r'expiring-link', ExpiringLinkViewSet, basename='expiringlink')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', views.obtain_auth_token)
]
