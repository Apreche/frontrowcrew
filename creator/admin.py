from django import forms
from django.contrib import admin

from . import models


class ChapterAdminForm(forms.ModelForm):
    class Meta:
        model = models.Chapter
        fields = "__all__"
        widgets = {
            "title": forms.TextInput
        }


@admin.register(models.Chapter)
class ChapterAdmin(admin.ModelAdmin):
    search_fields = ("episode__title",)
    form = ChapterAdminForm
    exclude = (
        "image_height",
        "image_width",
    )
    autocomplete_fields = ("episode",)
    list_display = (
        "episode",
        "title",
        "start_time"
    )
    date_hierarchy = "episode__pub_time"
    list_display_links = ("title",)
    list_filter = ("episode__show",)
    ordering = ("-episode__pub_time", "start_time",)


class ChapterInline(admin.StackedInline):
    model = models.Chapter
    form = ChapterAdminForm
    exclude = (
        "image_height",
        "image_width",
    )
    extra = 1


class EpisodeAdminForm(forms.ModelForm):
    class Meta:
        model = models.Episode
        fields = "__all__"
        widgets = {
            "title": forms.TextInput,
        }


@admin.register(models.Episode)
class EpisodeAdmin(admin.ModelAdmin):
    form = EpisodeAdminForm
    search_fields = (
        "title",
    )
    exclude = (
        "image_height",
        "image_width",
        "itunes_image_height",
        "itunes_image_width",
    )
    autocomplete_fields = (
        "mp3",
    )
    inlines = (
        ChapterInline,
    )
    readonly_fields = (
        "processed",
    )
    date_hierarchy = "pub_time"
    list_display = ("title", "show", "pub_time", "processed")
    list_filter = ("show",)
    ordering = ("-pub_time",)




class RelatedLinkAdminForm(forms.ModelForm):
    class Meta:
        model = models.RelatedLink
        fields = "__all__"
        widgets = {
            "title": forms.TextInput,
            "author": forms.TextInput,
        }


@admin.register(models.RelatedLink)
class RelatedLinkAdmin(admin.ModelAdmin):
    search_fields = ("title", "episode__title",)
    form = RelatedLinkAdminForm
    autocomplete_fields = ("episode",)
    date_hierarchy = "episode__pub_time"
    list_display = ("title", "episode",)
    list_filter = ("episode__show",)
    ordering = ("-episode__pub_time", "title")
