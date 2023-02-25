from django.contrib import admin

from . import models


class RelatedLinkInline(admin.TabularInline):
    model = models.RelatedLink


@admin.register(models.Show)
class ShowAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "sub_shows",
        "podcast",
    )
    exclude = (
        "logo_height",
        "logo_width",
        "thumbnail_height",
        "thumbnail_width",
    )


@admin.register(models.Content)
class ContentAdmin(admin.ModelAdmin):
    exclude = ("search_vector",)
    raw_id_fields = (
        "show",
        "podcast_episode",
    )
    inlines = [
        RelatedLinkInline
    ]


@admin.register(models.RelatedLinkType)
class RelatedLinkTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.RelatedLink)
class RelatedLinkAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "content",
        "type",
    )
