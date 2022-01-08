import markdown
from django import urls
from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import managers


class Publishable(models.Model):
    objects = models.Manager()
    published = managers.PublishedContentManager()

    is_published = models.BooleanField(default=False)
    pub_time = models.DateTimeField()

    class Meta:
        abstract = True


class Show(Publishable):
    title = models.TextField()
    slug = models.SlugField(max_length=255)
    logo = models.ImageField(upload_to="show/logos/")
    thumbnail = models.ImageField(upload_to="show/thumbnails/")
    display_in_nav = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return urls.reverse("show-detail", kwargs={"show_slug": self.slug})


class Content(Publishable):
    class Format(models.TextChoices):
        HTML = 'HTML', _("HTML")
        MARKDOWN = 'MD', _("Markdown")

    title = models.TextField()
    slug = models.SlugField(max_length=255)
    image = models.ImageField(upload_to="content/images/", blank=True, default="")
    show = models.ForeignKey(Show, on_delete=models.PROTECT)
    catalog_number = models.CharField(
        max_length=255,
        validators=[
            validators.RegexValidator(
                r"^\d+$",
                message=_("Catalog number may only contain digits")
            ),
        ]
    )

    creation_time = models.DateTimeField(auto_now_add=True)
    last_modified_time = models.DateTimeField(auto_now=True)

    rendered_html = models.TextField(blank=True)
    original_content = models.TextField(blank=True, default='')
    content_format = models.CharField(
        max_length=4,
        choices=Format.choices,
        default=Format.MARKDOWN,
    )

    class Meta:
        ordering = ['-pub_time']
        unique_together = (
            "show", "catalog_number"
        )

    def __str__(self):
        return self.title

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
        if self.content_format == self.Format.HTML:
            self.rendered_html = self.original_content
        elif self.content_format == self.Format.MARKDOWN:
            self.rendered_html = markdown.markdown(self.original_content)

    def save(self, *args, **kwargs):
        self._render_html()
        super().save(*args, **kwargs)
