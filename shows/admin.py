from django import forms
from django.contrib import admin


from . import models


class RelatedLinkTypeAdminForm(forms.ModelForm):
    class Meta:
        model = models.RelatedLinkType
        fields = "__all__"
        widgets = {
            "description": forms.TextInput,
            "plural_description": forms.TextInput,
        }


@admin.register(models.RelatedLinkType)
class RelatedLinkTypeAdmin(admin.ModelAdmin):
    form = RelatedLinkTypeAdminForm


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
    form = RelatedLinkAdminForm
    search_fields = (
        "content__title",
        "title",
    )
    autocomplete_fields = (
        "content",
    )
    list_display = (
        "title",
        "type",
        "content",
    )
    ordering = (
        "-content__pub_time",
        "type",
        "title",
    )
    date_hierarchy = "content__pub_time"
    list_filter = ("type",)


class RelatedLinkInlineAdminForm(forms.ModelForm):
    class Meta:
        model = models.RelatedLink
        fields = "__all__"
        widgets = {
            "title": forms.TextInput,
            "author": forms.TextInput,
            "description": forms.TextInput,
        }


class RelatedLinkInline(admin.TabularInline):
    model = models.RelatedLink
    form = RelatedLinkInlineAdminForm
    extra = 1


class ShowAdminForm(forms.ModelForm):
    class Meta:
        model = models.Show
        fields = "__all__"
        widgets = {
            "title": forms.TextInput,
        }


@admin.register(models.Show)
class ShowAdmin(admin.ModelAdmin):
    form = ShowAdminForm
    search_fields = ("title",)
    autocomplete_fields = (
        "podcast",
        "parent_show",
    )
    exclude = (
        "logo_height",
        "logo_width",
        "thumbnail_height",
        "thumbnail_width",
    )


class ContentAdminForm(forms.ModelForm):
    class Meta:
        model = models.Content
        fields = "__all__"
        widgets = {
            "title": forms.TextInput,
            "image_description": forms.TextInput,
        }


@admin.register(models.Content)
class ContentAdmin(admin.ModelAdmin):
    search_fields = (
        "title",
    )
    form = ContentAdminForm
    exclude = (
        "search_vector",
        "image_height",
        "image_width",
    )
    search_fields = (
        "title",
    )
    autocomplete_fields = (
        "show",
        "podcast_episode",
        "embedded_media",
        "related_content",
    )
    inlines = [
        RelatedLinkInline,
    ]
    list_display = (
        "title",
        "show",
        "pub_time",
    )
    date_hierarchy = "pub_time"
    list_filter = ("show",)
    ordering = ("-pub_time", "show", "title")
