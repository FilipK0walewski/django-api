from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group

from .models import Image, Tier, CustomUser


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_deisplay = ['image', 'owner']


@admin.register(Tier)
class ImageAdmin(admin.ModelAdmin):
    list_deisplay = ['name', 'sizes', 'original_image_access', 'expiring_link_access']


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'tier', 'is_admin']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords don\'t match')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ['username', 'tier', 'is_admin']


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ['username', 'tier']
    fieldsets = [
        (None, {'fields': ['username', 'password', 'tier']}),
        ('Permissions', {'fields': ['is_admin']}),
    ]
    add_fieldsets = [
        (
            None,
            {
                'classes': ['wide'],
                'fields': ['username', 'password1', 'password2', 'tier', 'is_admin'],
            },
        ),
    ]

admin.site.register(CustomUser, UserAdmin)
admin.site.unregister(Group)
