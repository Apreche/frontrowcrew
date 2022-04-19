from django import urls
from django.contrib.syndication import views as syndication_views

from podcasts import feeds as podcast_feeds
from podcasts import models as podcasts_models
from . import models


class ShowFeed(syndication_views.Feed):

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
