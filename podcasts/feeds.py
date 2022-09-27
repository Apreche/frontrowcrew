from django.contrib.sites import shortcuts as sites_shortcuts
from django.contrib.syndication import views

from . import models
from . import feedgenerator


class PodcastFeed(views.Feed):
    feed_type = feedgenerator.PodcastFeed

    def get_object(self, request, podcast_id):
        return models.Podcast.objects.select_related(
            "itunes_owner",
            "itunes_primary_category",
            "itunes_secondary_category",
        ).prefetch_related(
            "episodes",
            "episodes__chapters",
        ).get(id=podcast_id)

    def get_feed(self, obj, request):
        feed = super().get_feed(obj, request)
        # Inject current site into feed
        site = sites_shortcuts.get_current_site(request)
        protocol = "https" if request.is_secure() else "http"
        feed.feed["current_site"] = f"{protocol}://{site.domain}"
        feed.feed["current_site_name"] = site.name
        return feed

    # Feed Tags
    def title(self, obj):
        return obj.title

    def link(self, obj):
        return obj.get_absolute_url()

    def creative_commons_license(self, obj):
        return obj.creative_commons_license

    def description(self, obj):
        return obj.description

    def feed_copyright(self, obj):
        return obj.copyright

    def image(self, obj):
        return obj.image or None

    def image_description(self, obj):
        return obj.image_description or None

    def managing_editor(self, obj):
        return obj.managing_editor or None

    def ttl(self, obj):
        return obj.ttl

    def web_master(self, obj):
        return obj.web_master or None

    def itunes_author(self, obj):
        return obj.itunes_author

    def itunes_block(self, obj):
        return obj.itunes_block

    def itunes_categories(self, obj):
        return obj.itunes_categories

    def itunes_complete(self, obj):
        return obj.itunes_complete

    def itunes_explicit(self, obj):
        return obj.itunes_explicit

    def itunes_image(self, obj):
        return obj.itunes_image.url

    def itunes_new_feed_url(self, obj):
        return obj.itunes_new_feed_url

    def itunes_owner(self, obj):
        return obj.itunes_owner

    def itunes_title(self, obj):
        return obj.itunes_title

    def itunes_type(self, obj):
        return obj.itunes_type

    def feed_extra_kwargs(self, obj):
        extra = {}

        for field_name in [
            "creative_commons_license",
            "generator",
            "image",
            "image_description",
            "managing_editor",
            "web_master",

            "itunes_author",
            "itunes_block",
            "itunes_categories",
            "itunes_complete",
            "itunes_explicit",
            "itunes_image",
            "itunes_new_feed_url",
            "itunes_owner",
            "itunes_title",
            "itunes_type",
        ]:
            extra[field_name] = self._get_dynamic_attr(
                field_name, obj
            )
        return extra

    # Item Tags
    def items(self, obj):
        return models.PodcastEpisode.objects.select_related(
            "enclosure",
        ).prefetch_related(
            "chapters",
        ).filter(podcast=obj)[:100]

    def item_author_name(self, item):
        return item.author_name

    def item_author_email(self, item):
        return item.author_email

    def item_comments(self, item):
        return item.comments or None

    def item_chapters(self, item):
        return item.chapters.all()

    def item_description(self, item):
        return item.description

    def item_enclosure_url(self, item):
        return item.enclosure.url

    def item_enclosure_length(self, item):
        return item.enclosure.length

    def item_enclosure_mime_type(self, item):
        return item.enclosure.type

    def item_guid(self, item):
        return item.guid

    def item_guid_is_permalink(self, item):
        if not item.guid_is_permalink:
            return False
        return str(item.duration.seconds)

    def item_itunes_block(self, item):
        return item.itunes_block

    def item_itunes_duration(self, item):
        if item.duration is None:
            return None
        return str(item.duration.seconds)

    def item_itunes_episode_number(self, item):
        if item.itunes_episode_number is None:
            return None
        return str(item.itunes_episode_number)

    def item_itunes_episode_type(self, item):
        return item.itunes_episode_type

    def item_itunes_explicit(self, item):
        return item.itunes_explicit

    def item_itunes_image(self, item):
        itunes_image = item.itunes_image
        if itunes_image:
            return itunes_image.url
        image = item.image
        if image:
            return image.url
        return None

    def item_itunes_season_number(self, item):
        if item.itunes_season_number is None:
            return None
        return str(item.itunes_season_number)

    def item_itunes_title(self, item):
        return item.itunes_title

    def item_pubdate(self, item):
        return item.pub_date

    def item_title(self, item):
        return item.title

    def item_extra_kwargs(self, item):
        extra = {}
        for field_name in [
            "chapters",
            "itunes_duration",
            "itunes_episode_number",
            "itunes_episode_type",
            "itunes_image",
            "itunes_season_number",
            "itunes_title",
        ]:
            full_field_name = f"item_{field_name}"
            extra[full_field_name] = self._get_dynamic_attr(
                full_field_name, item
            )
        return extra
