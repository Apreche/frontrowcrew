from django.contrib import admin

from . import models


@admin.register(models.Show)
class ShowAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "sub_shows",
        "podcast",
    )


@admin.register(models.Content)
class ContentAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "show",
        "podcast_episode",
    )


@admin.register(models.RelatedLinkType)
class RelatedLinkTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.RelatedLink)
class RelatedLinkAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "content",
        "type",
    )
