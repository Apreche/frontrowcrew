from django.contrib import admin

from . import models


@admin.register(models.PodcastChapter)
class PodcastChapterAdmin(admin.ModelAdmin):
    search_fields = ("episode_title",)
    exclude = (
        "image_height",
        "image_width",
    )
    autocomplete_fields = (
        "episode",
    )
    list_display = (
        "episode",
        "title",
        "start_time"
    )
    date_hierarchy = "episode__pub_date"
    list_display_links = ("title",)
    list_filter = ("episode__podcast",)
    ordering = ("-episode__pub_date", "start_time",)


class PodcastChapterInline(admin.StackedInline):
    model = models.PodcastChapter
    exclude = (
        "image_height",
        "image_width",
    )
    extra = 1


@admin.register(models.Podcast)
class PodcastAdmin(admin.ModelAdmin):
    search_fields = ("title",)
    exclude = (
        "image_height",
        "image_width",
        "itunes_image_height",
        "itunes_image_width",
    )
    autocomplete_fields = (
        "itunes_primary_category",
        "itunes_secondary_category",
    )
    raw_id_fields = (
        "itunes_primary_category",
        "itunes_secondary_category",
    )


@admin.register(models.PodcastEpisode)
class PodcastEpisodeAdmin(admin.ModelAdmin):
    search_fields = ("title",)
    exclude = (
        "image_height",
        "image_width",
        "itunes_image_height",
        "itunes_image_width",
    )
    raw_id_fields = ("enclosure",)
    autocomplete_fields = (
        "podcast",
        "enclosure",
    )
    inlines = (
        PodcastChapterInline,
    )
    list_display = (
        "title",
        "podcast",
        "pub_date",
    )
    date_hierarchy = "pub_date"
    list_filter = ("podcast",)
    ordering = ("-pub_date", "podcast", "title")


@admin.register(models.iTunesCategory)
class iTunesCategoryAdmin(admin.ModelAdmin):
    search_fields = (
        "description",
        "subcategory_description",
    )
    list_filter = ("description",)
    ordering = ("description", "subcategory_description")


@admin.register(models.iTunesOwner)
class iTunesOwnerAdmin(admin.ModelAdmin):
    pass


@admin.register(models.PodcastEnclosure)
class PodcastEnclosureAdmin(admin.ModelAdmin):
    search_fields = ("url",)
