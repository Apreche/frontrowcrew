from django.db import models
from django.utils import timezone


class PublishedContentManager(models.Manager):

    def get_queryset(seflf):
        return super().get_queryset().filter(
            is_published=True,
            pub_time__lte=timezone.now(),
        )
