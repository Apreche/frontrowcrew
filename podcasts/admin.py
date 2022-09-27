from django.contrib import admin

from . import models


@admin.register(models.Podcast)
class PodcastAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "itunes_primary_category",
        "itunes_secondary_category",
    )
    exclude = (
        "image_height",
        "image_width",
        "itunes_image_height",
        "itunes_image_width",
    )


@admin.register(models.PodcastEpisode)
class PodcastEpisodeAdmin(admin.ModelAdmin):
    raw_id_fields = ("enclosure",)


@admin.register(models.iTunesCategory)
class iTunesCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.iTunesOwner)
class iTunesOwnerAdmin(admin.ModelAdmin):
    pass


@admin.register(models.PodcastEnclosure)
class PodcastEnclosureAdmin(admin.ModelAdmin):
    pass


@admin.register(models.PodcastChapter)
class PodcastChapterAdmin(admin.ModelAdmin):
    pass
