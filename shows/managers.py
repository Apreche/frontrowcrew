from django.apps import apps
from django.db import models
from django.utils import timezone


class PublishedManager(models.Manager):
    """ Easily filter only objects that are published """

    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=True,
            pub_time__lte=timezone.now(),
        )


class PublishedContentManager(models.Manager):
    """ Content is only published if its show is also published """

    def get_queryset(self):
        RelatedLink = apps.get_model("shows", "RelatedLink")
        RelatedLinkType = apps.get_model("shows", "RelatedLinkType")
        MetaData = apps.get_model("shows", "MetaData")
        MetaDataType = apps.get_model("shows", "MetaDataType")

        prefetches = []
        for related_link_type in RelatedLinkType.objects.all():
            prefetches.append(
                models.Prefetch(
                    "related_links",
                    queryset=RelatedLink.objects.filter(type=related_link_type),
                    to_attr=related_link_type.plural_slug,
                )
            )
        for meta_data_type in MetaDataType.objects.all():
            prefetches.append(
                models.Prefetch(
                    "metadata",
                    queryset=MetaData.objects.filter(type=meta_data_type),
                    to_attr=meta_data_type.plural_slug,
                )
            )

        return super().get_queryset(
        ).select_related(
            "show",
        ).prefetch_related(
            "tags",
            *prefetches,
        ).filter(
            is_published=True,
            show__is_published=True,
            pub_time__lte=timezone.now(),
            show__pub_time__lte=timezone.now(),
        )


class PublishedRelatedLinkManager(models.Manager):
    """ Related Links are only published if their content is also published """

    def get_queryset(self):
        return super().get_queryset().select_related(
            "content",
            "content__show",
        ).filter(
            content__is_published=True,
            content__show__is_published=True,
            content__pub_time__lte=timezone.now(),
            content__show__pub_time__lte=timezone.now(),
        )
