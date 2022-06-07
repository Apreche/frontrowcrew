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
        from .models import RelatedLinkType as RelatedLinkTypeConst
        RelatedLink = apps.get_model("shows", "RelatedLink")
        things_of_the_day = RelatedLink.published.filter(
            type_id=RelatedLinkTypeConst.THING_OF_THE_DAY
        )
        return super().get_queryset().select_related(
            "show"
        ).prefetch_related(
            models.Prefetch(
                "related_links",
                queryset=things_of_the_day,
                to_attr="things_of_the_day"
            ),
            "tags",
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
