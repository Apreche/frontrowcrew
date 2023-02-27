from django import forms
from django.contrib import admin
from . import models


@admin.register(models.MP3)
class MP3Admin(admin.ModelAdmin):
    search_fields = ("file",)


class FTPDestinationAdminForm(forms.ModelForm):
    class Meta:
        model = models.FTPDestination
        fields = "__all__"
        widgets = {
            "name": forms.TextInput,
            "host": forms.TextInput,
            "username": forms.TextInput,
            "password": forms.PasswordInput,
            "directory": forms.TextInput,
            "url_prefix": forms.TextInput,
        }


@admin.register(models.FTPDestination)
class FTPDestinationAdmin(admin.ModelAdmin):
    form = FTPDestinationAdminForm
