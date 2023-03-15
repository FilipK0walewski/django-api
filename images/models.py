import os

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, User
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils import timezone


class Tier(models.Model):
    name = models.CharField(unique=True, null=False, max_length=50)
    sizes = ArrayField(models.PositiveSmallIntegerField(unique=True))
    original_image_access = models.BooleanField(null=False, default=False)
    expiring_link_access = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        print('creating user', username, password)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username, password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(unique=True, max_length=50)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    tier = models.ForeignKey(Tier, blank=True, null=True, on_delete=models.CASCADE)

    USERNAME_FIELD = 'username'
    
    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def save(self, *args, **kwargs):
        if self.is_admin:
            self.is_staff = True
        super().save(*args, **kwargs)


def get_image_filename(instance, filename):
    return os.path.join('images', str(instance.owner.id), filename)


class Image(models.Model):
    image = models.ImageField(upload_to=get_image_filename, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class ExpiringLink(models.Model):
    image = models.ForeignKey(Image, null=False, on_delete=models.CASCADE)
    uuid = models.UUIDField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
