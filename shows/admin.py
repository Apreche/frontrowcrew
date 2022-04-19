from django.contrib import admin

from . import models


class ShowAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "sub_shows",
        "podcast",
    )


admin.site.register(models.Show, ShowAdmin)


class ContentAdmin(admin.ModelAdmin):
    raw_id_fields = (
        "show",
        "podcast_episode",
    )


admin.site.register(models.Content, ContentAdmin)
