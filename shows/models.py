import markdown
from django import urls
from django.contrib.postgres import indexes, search
from django.core import exceptions, validators
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from taggit import managers as taggit_managers

from . import managers


class Publishable(models.Model):
    """
    Publishable models have their visibility controlled
    via a boolean and a time.
    """
    objects = models.Manager()
    published = managers.PublishedManager()

    is_published = models.BooleanField(default=False)
    pub_time = models.DateTimeField()

    @property
    def is_live(self):
        """ Return True if the object is published """
        pub_time_past = self.pub_time <= timezone.now()
        return self.is_published and pub_time_past

    class Meta:
        abstract = True
        verbose_name = _("Publishable")
        verbose_name_plural = _("Publishables")
        get_latest_by = "pub_time"


class Show(Publishable):
    """
    A Show under which content will be grouped together.
    Most commonly, a podcast.
    """
    title = models.TextField()
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, default="")
    logo = models.ImageField(
        upload_to="shows/logo/",
        height_field="logo_height",
        width_field="logo_width",
        blank=True, default="",
    )
    logo_height = models.PositiveIntegerField(blank=True, null=True, default=None)
    logo_width = models.PositiveIntegerField(blank=True, null=True, default=None)
    thumbnail = models.ImageField(
        upload_to="shows/thumbnail/",
        height_field="thumbnail_height",
        width_field="thumbnail_width",
        blank=True, default="",
    )
    thumbnail_height = models.PositiveIntegerField(blank=True, null=True, default=None)
    thumbnail_width = models.PositiveIntegerField(blank=True, null=True, default=None)
    display_in_nav = models.BooleanField(default=False)

    podcast = models.OneToOneField(
        "podcasts.Podcast",
        blank=True, null=True, default=None,
        on_delete=models.PROTECT,
    )

    sub_shows = models.ManyToManyField(
        "self", symmetrical=False, blank=True,
        verbose_name=_("Sub-shows"),
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return urls.reverse("show-detail", kwargs={"show_slug": self.slug})

    @property
    def is_podcast(self):
        """ Teturn True if this Show is a podcast."""
        return self.podcast is not None

    @property
    def published_content(self):
        """
        Get all the published content for this show
        """
        if not self.is_live:
            # An unpublished show can never have published content
            return Content.objects.none()

        return Content.published.filter(
            models.Q(
                show=self
            ) | models.Q(
                show__in=self.sub_shows.all()
            )
        )

    class Meta:
        verbose_name = _("Show")
        verbose_name_plural = _("Shows")
        get_latest_by = "pub_time"


class Content(Publishable):
    """
    Individual content items belonging to a show.
    Most commonly, podcast episodes.
    """
    class Format(models.TextChoices):
        HTML = "HTML", _("HTML")
        MARKDOWN = "MD", _("Markdown")

    objects = models.Manager()
    published = managers.PublishedContentManager()
    tags = taggit_managers.TaggableManager()

    title = models.TextField()
    show = models.ForeignKey("shows.Show", on_delete=models.PROTECT)
    slug = models.SlugField(max_length=255)
    catalog_number = models.CharField(
        max_length=255,
        validators=[
            validators.RegexValidator(
                r"^\d+$",
                message=_("Catalog number may only contain digits")
            ),
        ],
    )
    image = models.ImageField(
        upload_to="shows/content/image/",
        height_field="image_height",
        width_field="image_width",
        blank=True,
        default="",
    )
    image_description = models.TextField(blank=True, default="")
    image_height = models.PositiveIntegerField(blank=True, null=True, default=None)
    image_width = models.PositiveIntegerField(blank=True, null=True, default=None)

    creation_time = models.DateTimeField(auto_now_add=True)
    last_modified_time = models.DateTimeField(auto_now=True)

    rendered_html = models.TextField(blank=True)
    original_content = models.TextField(blank=True, default="")
    content_format = models.CharField(
        max_length=4,
        choices=Format.choices,
        default=Format.MARKDOWN,
    )

    podcast_episode = models.OneToOneField(
        "podcasts.PodcastEpisode",
        blank=True, null=True, default=None,
        on_delete=models.PROTECT,
    )

    embedded_media = models.ManyToManyField("embeds.Media")

    related_content = models.ManyToManyField("self")

    search_vector = search.SearchVectorField(
        editable=False
    )

    def __str__(self):
        return self.title

    def clean(self):
        """ Validate the data on this content item. """
        if self.podcast_episode is not None:
            if self.show.podcast is None:
                raise exceptions.ValidationError(
                    {
                        "podcast_episode": _(
                            "Podcast episode may not be set if show is not a podcast."
                        )
                    }
                )
            elif self.show.podcast != self.podcast_episode.podcast:
                raise exceptions.ValidationError(
                    {
                        "podcast_episode": _(
                            "Podcast episode does not belong to same podcast as show."
                        )
                    }
                )
        if self.is_published and not self.show.is_published:
            raise exceptions.ValidationError(
                {
                    "is_published": _(
                        "Content can not be published if show is not published."
                    )
                }
            )

    def get_absolute_url(self):
        return urls.reverse(
            "content-detail",
            kwargs={
                "show_slug": self.show.slug,
                "catalog_number": self.catalog_number,
                "content_slug": self.slug,
            }
        )

    def _render_html(self):
        """ Render the final HTML from the source according to the chosen format """
        if self.content_format == self.Format.HTML:
            self.rendered_html = self.original_content
        elif self.content_format == self.Format.MARKDOWN:
            self.rendered_html = markdown.markdown(self.original_content)

    @property
    def is_live(self):
        """ Content is only published if its parent show is also published """
        pub_time_past = self.pub_time <= timezone.now()
        return self.show.is_live and self.is_published and pub_time_past

    def save(self, *args, **kwargs):
        """ Render the html when the content is written to the DB """
        self._render_html()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Content")
        verbose_name_plural = _("Contents")
        get_latest_by = "pub_time"
        ordering = ["-pub_time"]
        unique_together = [
            ("show", "catalog_number"),
        ]
        indexes = [
            indexes.GinIndex(fields=["search_vector"])
        ]

    class ReadonlyMeta:
        readonly = ["search_vector"]


class RelatedLinkType(models.Model):
    """
    What kind of relation ship does a RelatedLink have with its content?
    """
    THING_OF_THE_DAY = 1
    FORUM_THREAD = 2
    PURCHASE_LINK = 3

    description = models.TextField(unique=True)
    plural_description = models.TextField(unique=True)
    slug = models.SlugField(unique=True)
    plural_slug = models.SlugField(unique=True)

    def __str__(self):
        return self.description


class RelatedLink(models.Model):
    """
    A link related to a piece of content.
    """
    objects = models.Manager()
    published = managers.PublishedRelatedLinkManager()

    content = models.ForeignKey(
        "shows.Content", on_delete=models.PROTECT,
        related_name="related_links",
    )
    type = models.ForeignKey(
        "shows.RelatedLinkType", on_delete=models.PROTECT
    )
    title = models.TextField()
    description = models.TextField(blank=True, default="")
    url = models.URLField()
    author = models.TextField()
    error = models.BooleanField(default=False)

    def get_absolute_url(self):
        return self.url

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Related Link")
        verbose_name_plural = _("Related Links")
        ordering = ["-content__pub_time", "author"]


class MetaDataType(models.Model):
    """
    What type of metadata is this?
    """
    BOOK_AUTHOR = 1

    description = models.TextField(unique=True)
    plural_description = models.TextField(unique=True)
    slug = models.SlugField(unique=True)
    plural_slug = models.SlugField(unique=True)

    def __str__(self):
        return self.description


class MetaData(models.Model):
    content = models.ForeignKey(
        "shows.Content", on_delete=models.PROTECT,
        related_name="metadata",
    )
    type = models.ForeignKey(
        "shows.MetaDataType", on_delete=models.PROTECT
    )
    data = models.TextField()
