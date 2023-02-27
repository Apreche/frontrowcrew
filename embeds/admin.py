from django import forms
from django.contrib import admin

from . import models


class ServiceAdminForm(forms.ModelForm):
    class Meta:
        model = models.Service
        fields = "__all__"
        widgets = {
            "name": forms.TextInput,
        }


@admin.register(models.Service)
class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm


class MediaAdminForm(forms.ModelForm):
    class Meta:
        model = models.Media
        fields = "__all__"
        widgets = {
            "description": forms.TextInput,
            "media_id": forms.TextInput,
        }


@admin.register(models.Media)
class MediaAdmin(admin.ModelAdmin):
    form = MediaAdminForm
    search_fields = ("description",)
    list_display = ("description", "service",)
    list_filter = ("service",)
    ordering = ("service", "description",)
