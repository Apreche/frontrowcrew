from django import http
from django import urls
from django.contrib.syndication import views as syndication_views
from django.utils.translation import gettext as _

from podcasts import feeds as podcast_feeds
from podcasts import models as podcasts_models
from . import models


class ShowFeed(syndication_views.Feed):
    """ A feed of all published content for a particular show """

    # Channel Level
    def get_object(self, request, show_slug):
        return models.Show.published.get(
            slug=show_slug
        )

    def title(self, obj):
        return obj.title

    def link(self, obj):
        return obj.get_absolute_url()

    def feed_url(self, obj):
        return urls.reverse(
            "show-rss",
            kwargs={"show_slug": obj.slug}
        )

    def feed_guid(self, obj):
        return self.feed_url(obj)

    def description(self, obj):
        return obj.description

    # Item level
    def items(self, obj):
        return obj.published_content.order_by(
            "-pub_time"
        )[:100]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.rendered_html

    def item_pubdate(self, item):
        return item.pub_time

    def item_updatedate(self, item):
        return item.last_modified_time


class ShowPodcastFeed(podcast_feeds.PodcastFeed):
    """ A feed of all content for a particular show with full podcast enclosures and spec """

    def get_object(self, request, show_slug):
        return podcasts_models.Podcast.objects.select_related(
            "show",
            "itunes_owner",
            "itunes_primary_category",
            "itunes_secondary_category",
        ).get(
            show=models.Show.published.get(
                slug=show_slug,
                podcast__isnull=False,
            )
        )

    def link(self, obj):
        return obj.show.get_absolute_url()

    def feed_url(self, obj):
        return urls.reverse(
            "show-rss",
            kwargs={"show_slug": obj.show.slug}
        )

    def items(self, obj):
        return podcasts_models.PodcastEpisode.objects.filter(
            content__in=obj.show.published_content.filter(
                podcast_episode__isnull=False,
            )
        ).order_by("-content__pub_time")[:100]


class TotDFeed(syndication_views.Feed):
    """ A feed of all the Things of the Day """

    # Channel Level
    title = _("GeekNights Things of the Day")
    description = _(
        "A compilation of all the links selected "
        "in the Things of the Day segment of "
        "the GeekNights podcast."
    )

    def link(self):
        return urls.reverse("totd-list")

    def feed_url(self):
        return urls.reverse("totd-list-rss")

    # Item level
    def items(self):
        items = models.RelatedLink.published.select_related(
            "content"
        ).filter(
            type_id=models.RelatedLinkType.THING_OF_THE_DAY
        )
        if not items:
            raise http.Http404(_("No things of the day found."))
        return items

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return item.url

    def item_author_name(self, item):
        return item.author

    def item_pubdate(self, item):
        return item.content.pub_time
