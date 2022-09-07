from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit import managers as taggit_managers
from podcasts import models as podcast_models


class Episode(models.Model):
    """
    A podcast episode that the user has requested be created.
    Exists as a log of episodes user has submitted.
    Also, the tasks that create the actual episode refer to this
    as the source of original data.
    """
    processed = models.BooleanField(default=False)
    mp3 = models.ForeignKey(
        "media.MP3",
        on_delete=models.PROTECT
    )
    destination = models.ForeignKey(
        "media.FTPDestination",
        on_delete=models.PROTECT,
    )
    show = models.ForeignKey(
        "shows.Show",
        on_delete=models.PROTECT,
    )
    title = models.TextField()

    catalog_number = models.CharField(
        max_length=255,
        validators=[
            validators.RegexValidator(
                r"^\d+$",
                message=_("Catalog number may only contain digits")
            ),
        ],
    )
    pub_time = models.DateTimeField()
    tags = taggit_managers.TaggableManager()
    description = models.TextField(max_length=4000, blank=True, default="")
    body = models.TextField()
    author_name = models.CharField(max_length=255, blank=True, default="")
    author_email = models.EmailField(blank=True, default="")
    image = models.ImageField(
        upload_to="creator/episode/image",
        height_field="image_height",
        width_field="image_width",
        blank=True,
        default="",
    )
    image_description = models.TextField(blank=True, default="")
    image_height = models.PositiveIntegerField(blank=True, null=True, default=None)
    image_width = models.PositiveIntegerField(blank=True, null=True, default=None)
    itunes_title = models.CharField(
        max_length=255, blank=True, default="",
    )
    itunes_image = models.ImageField(
        upload_to="creator/episode/itunes_image",
        height_field="itunes_image_height",
        width_field="itunes_image_width",
        blank=True,
        default="",
    )
    itunes_image_description = models.TextField(blank=True, default="")
    itunes_image_height = models.PositiveIntegerField(blank=True, null=True, default=None)
    itunes_image_width = models.PositiveIntegerField(blank=True, null=True, default=None)
    itunes_episode_number = models.PositiveIntegerField(
        blank=True, null=True, default=None,
    )
    itunes_season_number = models.PositiveIntegerField(
        blank=True, null=True, default=None,
    )
    itunes_explicit = models.BooleanField(null=True, default=None)
    itunes_episode_type = models.CharField(
        max_length=255,
        choices=podcast_models.PodcastEpisode.EpisodeType.choices,
        blank=True,
        default=podcast_models.PodcastEpisode.EpisodeType.DEFAULT,
    )
    itunes_block = models.BooleanField(default=False)


class RelatedLink(models.Model):
    episode = models.ForeignKey(
        "creator.Episode",
        on_delete=models.CASCADE,
        related_name="related_links",
    )
    title = models.TextField()
    url = models.URLField()
    author = models.TextField()
    description = models.TextField(blank=True, default="")


class Chapter(models.Model):
    episode = models.ForeignKey(
        "creator.Episode",
        on_delete=models.CASCADE,
        related_name="chapters",
    )
    start_time = models.PositiveIntegerField()
    end_time = models.PositiveIntegerField(blank=True, null=True, default=None)
    title = models.TextField()
    description = models.TextField(blank=True, default="")
    url = models.URLField(blank=True, default="")
    url_description = models.TextField(blank=True, default="")
    image = models.ImageField(
        upload_to="creator/chapter/image",
        height_field="image_height",
        width_field="image_width",
        blank=True,
        default="",
    )
    image_height = models.PositiveIntegerField(blank=True, null=True, default=None)
    image_width = models.PositiveIntegerField(blank=True, null=True, default=None)
    image_description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ("episode", "start_time")
