import uuid
from django import urls
from django.core import exceptions
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models import Q, constraints


class iTunesCategory(models.Model):
    description = models.CharField(max_length=255, default="")
    subcategory_description = models.CharField(
        max_length=255, blank=True, default=""
    )

    @property
    def is_subcategory(self):
        return bool(self.subcategory_description)

    def __str__(self):
        if not self.subcategory_description:
            return self.description
        else:
            return f"{self.description}::{self.subcategory_description}"

    class Meta:
        verbose_name = "iTunes Category"
        verbose_name_plural = "iTunes Categories"
        unique_together = ["description", "subcategory_description"]


class iTunesOwner(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} <{self.email}>"

    class Meta:
        verbose_name = "iTunes Owner"
        verbose_name_plural = "iTunes Owners"
        unique_together = ["name", "email"]


class Podcast(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=4000)
    language = models.CharField(
        max_length=2, default="en",
        help_text=_("ISO 639-1"),
    )
    managing_editor = models.EmailField(blank=True, default="")
    web_master = models.EmailField(blank=True, default="")
    ttl = models.PositiveIntegerField(null=True, default=None)
    image = models.ImageField(
        upload_to="podcasts/podcast/image/",
        height_field="image_height",
        width_field="image_width",
        blank=True, default="",
    )
    image_height = models.PositiveIntegerField(blank=True, null=True, default=None)
    image_width = models.PositiveIntegerField(blank=True, null=True, default=None)
    image_description = models.TextField(blank=True, default="")
    itunes_image = models.ImageField(
        upload_to="podcasts/podcast/itunes_image/",
        height_field="itunes_image_height",
        width_field="itunes_image_width",
    )
    itunes_image_height = models.PositiveIntegerField()
    itunes_image_width = models.PositiveIntegerField()
    itunes_primary_category = models.ForeignKey(
        iTunesCategory, on_delete=models.PROTECT,
        related_name="+",
    )
    itunes_secondary_category = models.ForeignKey(
        iTunesCategory, on_delete=models.PROTECT,
        null=True, blank=True, default=None,
        related_name="+",
    )
    itunes_explicit = models.BooleanField(null=True, default=None)

    itunes_author = models.CharField(max_length=255)
    itunes_owner = models.ForeignKey(
        iTunesOwner, blank=True, null=True, default=None,
        on_delete=models.PROTECT,
    )

    itunes_title = models.CharField(
        max_length=255, blank=True, default="",
        help_text=_("Optional alternate feed title for iTunes"),
    )

    class PodcastType(models.TextChoices):
        DEFAULT = "", _("Default")
        EPISODIC = "episodic", _("Episodic")
        SERIAL = "serial", _("Serial")

    itunes_type = models.CharField(
        max_length=255,
        choices=PodcastType.choices,
        default=PodcastType.DEFAULT,
        blank=True,
    )
    itunes_block = models.BooleanField(
        default=False,
        help_text=_("Block directories from including this podcast."),
    )
    itunes_complete = models.BooleanField(
        default=False,
        help_text=_("This podcast is DONE (will never have a new episode)."),
    )
    itunes_new_feed_url = models.URLField(
        blank=True, default="",
        help_text=_("Use this for moving the podcast RSS URL"),
    )
    copyright = models.CharField(max_length=255, blank=True, default="")
    creative_commons_license = models.URLField(blank=True, default="")

    @property
    def itunes_categories(self):
        categories = [
            self.itunes_primary_category,
            self.itunes_secondary_category
        ]
        return [c for c in categories if c is not None]

    def get_absolute_url(self):
        return urls.reverse(
            "podcast-rss",
            kwargs={
                "podcast_id": self.id,
            }
        )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Podcast"
        verbose_name_plural = "Podcasts"


class PodcastEnclosure(models.Model):

    class EnclosureType(models.TextChoices):
        M4A = "audio/x-m4a", _("M4A")
        MP3 = "audio/mpeg", _("MP3")
        MOV = "video/quicktime", _("MOV")
        MP4 = "video/mp4", _("MP4")
        M4V = "video/x-m4v", _("M4V")
        PDF = "application/pdf", _("PDF")

    url = models.URLField(unique=True)
    length = models.PositiveBigIntegerField(
        help_text=_("Size of file in bytes"),
    )
    type = models.CharField(
        max_length=255,
        choices=EnclosureType.choices,
        default=EnclosureType.MP3,
    )

    def __str__(self):
        return self.url

    class Meta:
        verbose_name = "Podcast Enclosure"
        verbose_name_plural = "Podcast Enclosures"


class PodcastEpisode(models.Model):
    podcast = models.ForeignKey(
        Podcast, on_delete=models.PROTECT,
        related_name="episodes",
        related_query_name="episode",
    )
    title = models.CharField(max_length=255)
    enclosure = models.ForeignKey(PodcastEnclosure, on_delete=models.PROTECT)

    guid = models.CharField(max_length=255, blank=True, default=uuid.uuid4)
    guid_is_permalink = models.BooleanField(default=False)
    pub_date = models.DateTimeField(blank=True, default=None)
    description = models.TextField(max_length=4000, blank=True, default="")
    duration = models.DurationField(
        blank=True, null=True, default=None
    )
    author_name = models.CharField(max_length=255, blank=True, default="")
    author_email = models.EmailField(blank=True, default="")
    comments = models.URLField(blank=True, default="")
    itunes_image = models.ImageField(
        upload_to="podcasts/podcastepisodes/itunes_image/",
        height_field="itunes_image_height",
        width_field="itunes_image_width",
        blank=True, default="",
    )
    itunes_image_height = models.PositiveIntegerField(blank=True, null=True, default=None)
    itunes_image_width = models.PositiveIntegerField(blank=True, null=True, default=None)
    itunes_explicit = models.BooleanField(null=True, default=None)

    itunes_title = models.CharField(
        max_length=255, blank=True, default="",
        help_text=_("Optional alternate episode title for iTunes"),
    )
    itunes_episode_number = models.PositiveIntegerField(
        blank=True, null=True, default=None,
        help_text=_("Episode Number, required for serial shows"),
    )
    itunes_season_number = models.PositiveIntegerField(
        blank=True, null=True, default=None,
        help_text=_("Season Number"),
    )

    class EpisodeType(models.TextChoices):
        DEFAULT = "", _("Default")
        FULL = "full", _("Full")
        TRAILER = "trailer", _("Trailer")
        BONUS = "bonus", _("Bonus")

    itunes_episode_type = models.CharField(
        max_length=255,
        choices=EpisodeType.choices,
        blank=True,
        default=EpisodeType.DEFAULT,
    )
    itunes_block = models.BooleanField(
        default=False,
        help_text=_("Block directories from including this episode.")
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return self.enclosure.url

    def clean(self):
        if self.podcast.itunes_type == Podcast.PodcastType.SERIAL:
            if self.itunes_episode_number is None:
                raise exceptions.ValidationError(
                    {
                        "itunes_episode_number": exceptions.ValidationError(
                            _("Episode numbers are required for serial podcasts."),
                            code="required",
                        )
                    }
                )

    class Meta:
        verbose_name = "Podcast Episode"
        verbose_name_plural = "Podcast Episodes"
        constraints = [
            constraints.UniqueConstraint(
                fields=["podcast", "itunes_episode_number", "itunes_season_number"],
                condition=Q(itunes_episode_number__isnull=False) | Q(itunes_season_number__isnull=False),
                name="unique_podcast_season_and_episode_when_set"
            ),
        ]


class PodcastChapter(models.Model):
    episode = models.ForeignKey(
        PodcastEpisode, on_delete=models.PROTECT,
        related_name="chapters",
        related_query_name="chapter",
    )
    start_time = models.PositiveIntegerField()
    end_time = models.PositiveIntegerField(blank=True, null=True, default=None)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, default="")
    url = models.URLField(blank=True, default="")
    image = models.ImageField(
        upload_to="podcasts/podcastchapters/image/",
        height_field="image_height",
        width_field="image_width",
        blank=True, default="",
        help_text=_("Aspect ratio must be 1:1."),
    )
    image_height = models.PositiveIntegerField(blank=True, null=True, default=None)
    image_width = models.PositiveIntegerField(blank=True, null=True, default=None)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Podcast Chapter"
        verbose_name_plural = "Podcast Chapters"
