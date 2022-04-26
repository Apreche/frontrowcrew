from django.contrib import admin

from . import models


class PodcastAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "itunes_primary_category",
        "itunes_secondary_category",
    )


admin.site.register(models.Podcast, PodcastAdmin)


class PodcastEpisodeAdmin(admin.ModelAdmin):
    raw_id_fields = ("enclosure",)


admin.site.register(models.PodcastEpisode, PodcastEpisodeAdmin)


class iTunesCategoryAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.iTunesCategory, iTunesCategoryAdmin)


class iTunesOwnerAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.iTunesOwner, iTunesOwnerAdmin)


class PodcastEnclosureAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.PodcastEnclosure, PodcastEnclosureAdmin)


class PodcastChapterAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.PodcastChapter, PodcastChapterAdmin)
