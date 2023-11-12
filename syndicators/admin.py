from django.contrib import admin

from . import models


@admin.register(models.Discord)
class DiscordAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Discourse)
class DiscourseAdmin(admin.ModelAdmin):
    pass
