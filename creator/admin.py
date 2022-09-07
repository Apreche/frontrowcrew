from django.contrib import admin

from . import models


@admin.register(models.Episode)
class EpisodeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Chapter)
class ChapterAdmin(admin.ModelAdmin):
    pass


@admin.register(models.RelatedLink)
class RelatedLinkAdmin(admin.ModelAdmin):
    pass
