from django.db import models
from django.utils import timezone


class PublishedManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=True,
            pub_time__lte=timezone.now(),
        )


class PublishedContentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            "show"
        ).filter(
            is_published=True,
            show__is_published=True,
            pub_time__lte=timezone.now(),
            show__pub_time__lte=timezone.now(),
        )
