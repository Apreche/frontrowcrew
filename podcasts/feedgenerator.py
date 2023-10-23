from typing import Any, Dict

from django.utils import feedgenerator, xmlutils

from podcasts import utils


class PodcastFeed(feedgenerator.Rss201rev2Feed):
    def rss_attributes(self) -> Dict[Any, Any]:
        attrs = super().rss_attributes()
        attrs['xmlns:itunes'] = "http://www.itunes.com/dtds/podcast-1.0.dtd"
        attrs['xmlns:content'] = "http://purl.org/rss/1.0/modules/content/"
        attrs['xmlns:creativeCommons'] = "http://backend.userland.com/creativeCommonsRssModule"
        return attrs

    def add_root_elements(self, handler: xmlutils.SimplerXMLGenerator) -> None:
        ###
        # https://github.com/django/django/blob/4.0.3/django/utils/feedgenerator.py
        # COPY/PASTE insetad of super() because of description
        current_site = self.feed.get("current_site", None)
        current_site_name = self.feed.get("current_site_name", None)

        handler.addQuickElement("title", self.feed["title"])
        handler.addQuickElement("link", self.feed["link"])
        # handler.addQuickElement("description", self.feed["description"])
        if self.feed["feed_url"] is not None:
            handler.addQuickElement(
                "atom:link", None, {"rel": "self", "href": self.feed["feed_url"]}
            )
        if self.feed["language"] is not None:
            handler.addQuickElement("language", self.feed["language"])
        for cat in self.feed["categories"]:
            handler.addQuickElement("category", cat)
        if self.feed["feed_copyright"] is not None:
            handler.addQuickElement("copyright", self.feed["feed_copyright"])
        handler.addQuickElement(
            "lastBuildDate", feedgenerator.rfc2822_date(self.latest_post_date())
        )
        if self.feed["ttl"] is not None:
            handler.addQuickElement("ttl", self.feed["ttl"])
        # END COPY/PASTE
        ###

        # Simple Tags
        simple_elements = [
            ("creative_commons_license", "creativeCommons:license"),
            ("managing_editor", "managingEditor"),
            ("web_master", "webMaster"),
            ("itunes_author", "itunes:author"),
            ("itunes_new_feed_url", "itunes:new-feed-url"),
            ("itunes_title", "itunes:title"),
            ("itunes_type", "itunes:type"),
        ]
        for key, tag in simple_elements:
            value = self.feed.get(key, None)
            if value:
                handler.addQuickElement(tag, value)

        # Generator
        generator_value = self.feed.get("generator", current_site_name)
        handler.addQuickElement("generator", generator_value)

        # CDATA description
        description = self.feed.get("description", None)
        if description:
            handler.startElement("description", {})
            cdata = f"<![CDATA[{description}]]>"
            handler.ignorableWhitespace(cdata)
            handler.endElement("description")

        # RSS Image
        image = self.feed.get("image", None)
        if image:
            handler.startElement("image", {})
            handler.addQuickElement("title", self.feed["title"])
            handler.addQuickElement("link", current_site)
            handler.addQuickElement("url", image.url)
            handler.addQuickElement("width", str(image.width))
            handler.addQuickElement("height", str(image.height))
            image_description = self.feed.get("image_description", None)
            if image_description:
                handler.addQuickElement("description", image_description)
            handler.endElement("image")

        # iTunes Block and Complete
        itunes_block = self.feed.get("itunes_block", False)
        if itunes_block:
            handler.addQuickElement("itunes:block", "Yes")
        itunes_complete = self.feed.get("itunes_complete", False)
        if itunes_complete:
            handler.addQuickElement("itunes:complete", "Yes")

        # iTunes Categories
        itunes_categories = self.feed.get("itunes_categories", [])
        for category in itunes_categories[:2]:
            if category.is_subcategory:
                handler.startElement(
                    "itunes:category",
                    {
                        "text": category.description,
                    }
                )
                handler.addQuickElement(
                    "itunes:category",
                    attrs={
                        "text": category.subcategory_description,
                    }
                )
                handler.endElement("itunes:category")
            else:
                handler.addQuickElement(
                    "itunes:category",
                    attrs={
                        "text": category.description,
                    }
                )

        # iTunes Explicit
        itunes_explicit = self.feed.get("itunes_explicit", None)
        if itunes_explicit is not None:
            if itunes_explicit:
                handler.addQuickElement("itunes:explicit", "true")
            else:
                handler.addQuickElement("itunes:explicit", "false")

        # iTunesImage
        itunes_image = self.feed.get("itunes_image", None)
        if itunes_image is not None:
            handler.addQuickElement(
                "itunes:image",
                contents=None,
                attrs={"href": itunes_image},
            )

        # iTunesOwner
        itunes_owner = self.feed.get("itunes_owner", None)
        if itunes_owner:
            handler.startElement("itunes:owner", {})
            handler.addQuickElement("itunes:name", itunes_owner.name)
            handler.addQuickElement("itunes:email", itunes_owner.email)
            handler.endElement("itunes:owner")

    def item_attributes(self, item: Dict[str, Any]) -> Dict[Any, Any]:
        return super().item_attributes(item)

    def add_item_elements(self, handler: xmlutils.SimplerXMLGenerator, item: Dict[str, Any]) -> None:
        simple_elements = [
            ("item_itunes_episode_number", "itunes:episode"),
            ("item_itunes_episode_type", "itunes:episodeType"),
            ("item_itunes_duration", "itunes:duration"),
            ("item_itunes_season_number", "itunes:season"),
            ("item_itunes_title", "itunes:title"),
        ]
        for key, tag in simple_elements:
            value = item.get(key, None)
            if value:
                handler.addQuickElement(tag, value)

        # CDATA Item description
        description = item.get("description", None)
        if description:
            handler.startElement("description", {})
            cdata = f"<![CDATA[{description}]]>"
            handler.ignorableWhitespace(cdata)
            handler.endElement("description")

        # iTunes Item Image
        itunes_image = item.get("itunes_image", None)
        if itunes_image is not None:
            handler.addQuickElement(
                "itunes:image",
                contents=None,
                attrs={"href": itunes_image},
            )

        # iTunes Item Explicit
        itunes_explicit = item.get("item_itunes_explicit", None)
        if itunes_explicit is not None:
            if itunes_explicit:
                handler.addQuickElement("itunes:explicit", "true")
            else:
                handler.addQuickElement("itunes:explicit", "false")

        # iTunes Item Block
        itunes_block = item.get("item_itunes_block", False)
        if itunes_block:
            handler.addQuickElement("itunes:block", "Yes")

        # Chapters
        chapters = item.get("item_chapters", None)
        if chapters:
            handler.startElement(
                "psc:chapters",
                {
                    "version": "1.2",
                    "xmlns:psc": "http://podlove.org/simple-chapters/",
                }
            )
            for chapter in chapters:
                chapter_attrs = {}
                start_time = utils.milliseconds_to_timespan(chapter.start_time)
                chapter_attrs["start"] = start_time
                chapter_attrs["title"] = chapter.title
                url = getattr(chapter, "url", None)
                if url:
                    chapter_attrs["href"] = url
                image = getattr(chapter, "image", None)
                if image:
                    chapter_attrs["image"] = image.url
                handler.addQuickElement(
                    "psc:chapter", None, chapter_attrs
                )
            handler.endElement("psc:chapters")

        # Set description to None to avoid double description
        item["description"] = None

        return super().add_item_elements(handler, item)
