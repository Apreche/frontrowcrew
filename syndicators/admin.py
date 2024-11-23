from django import forms
from django.contrib import admin

from . import models


class BlueskyForm(forms.ModelForm):
    class Meta:
        model = models.Bluesky
        widgets = {
            "password": forms.PasswordInput(),
        }
        fields = "__all__"


@admin.register(models.Bluesky)
class BlueskyAdmin(admin.ModelAdmin):
    form = BlueskyForm


@admin.register(models.Discord)
class DiscordAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Discourse)
class DiscourseAdmin(admin.ModelAdmin):
    pass
