import os
import random
import tempfile

from http import HTTPStatus
from xml import etree

from django import test, urls
from django.contrib.sites.models import Site

from podcasts.tests.utils import skip_if_invalid_rss_xml
from .. import factories
from .. import urls as podcast_urls


@test.override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "betafrc_test_media"),
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    ROOT_URLCONF=podcast_urls,
)
class PodcastsFeedTests(test.TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.podcast = factories.PodcastFactory.create()
        cls.url = urls.reverse(
            "podcast-rss",
            kwargs={"podcast_id": cls.podcast.id}
        )
        for _ in range(random.randint(0, 10)):
            factories.PodcastEpisodeFactory(
                podcast=cls.podcast
            )
        cls.xml_namespaces = {
            "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
            "content": "http://purl.org/rss/1.0/modules/content/",
            "creativeCommons": "http://backend.userland.com/creativeCommonsRssModule",
            "psc": "http://podlove.org/simple-chapters/",
        }

    def setUp(self):
        self.response = self.client.get(self.url)
        if self.response.status_code == HTTPStatus.OK:
            try:
                self.etree = etree.ElementTree.fromstring(self.response.content)
            except Exception as etree_exception:
                self.etree_exception = etree_exception

    def test_feed_ok(self):
        self.assertEqual(self.response.status_code, HTTPStatus.OK)

    def test_etree_ok(self):
        if self.response.status_code != HTTPStatus.OK:
            self.skipTest("Skip because of failed request.")
        etree_exception = getattr(self, "etree_exception", None)
        self.assertIsNone(etree_exception)

    @skip_if_invalid_rss_xml
    def test_itunes_title(self):
        channel = self.etree.find("channel")
        self.assertIsNotNone(channel)
        title = channel.find("title")
        self.assertIsNotNone(title)
        self.assertEqual(title.text, self.podcast.title)

    @skip_if_invalid_rss_xml
    def test_itunes_link(self):
        channel = self.etree.find("channel")
        self.assertIsNotNone(channel)
        link = channel.find("link")
        self.assertIsNotNone(link)
        self.assertTrue(link.text.endswith(self.url))

    @skip_if_invalid_rss_xml
    def test_creative_commons_license(self):
        channel = self.etree.find("channel")
        self.assertIsNotNone(channel)
        creative_commons_license = channel.find(
            "creativeCommons:license",
            namespaces=self.xml_namespaces,
        )
        if not self.podcast.creative_commons_license:
            self.assertIsNone(creative_commons_license)
        else:
            self.assertIsNotNone(creative_commons_license)
            self.assertEqual(
                creative_commons_license.text,
                self.podcast.creative_commons_license
            )

    @skip_if_invalid_rss_xml
    def test_description(self):
        channel = self.etree.find("channel")
        self.assertIsNotNone(channel)
        description = channel.find("description")
        self.assertEqual(description.text, self.podcast.description)

    @skip_if_invalid_rss_xml
    def test_image(self):
        channel = self.etree.find("channel")
        self.assertIsNotNone(channel)
        image = channel.find("image")
        if not self.podcast.image:
            self.assertIsNone(image)
        else:
            self.assertIsNotNone(image)
            image_title = image.find("title")
            self.assertEqual(image_title.text, self.podcast.title)
            image_link = image.find("link")
            protocol = self.response.request["wsgi.url_scheme"]
            site = Site.objects.get_current()
            link = f"{protocol}://{site.domain}"
            self.assertEqual(image_link.text, link)
            image_url = image.find("url")
            self.assertEqual(image_url.text, self.podcast.image.url)
            image_width = image.find("width")
            self.assertEqual(image_width.text, str(self.podcast.image.width))
            self.assertEqual(image_width.text, str(self.podcast.image_width))
            image_height = image.find("height")
            self.assertEqual(image_height.text, str(self.podcast.image.height))
            self.assertEqual(image_height.text, str(self.podcast.image_height))

    @skip_if_invalid_rss_xml
    def test_itunes_block(self):
        channel = self.etree.find("channel")
        self.assertIsNotNone(channel)
        itunes_block = channel.find(
            "itunes:block",
            namespaces=self.xml_namespaces,
        )
        if self.podcast.itunes_block:
            self.assertIsNotNone(itunes_block)
            self.assertEqual(itunes_block.text, "Yes")
        else:
            self.assertIsNone(itunes_block)

    @skip_if_invalid_rss_xml
    def test_itunes_complete(self):
        channel = self.etree.find("channel")
        self.assertIsNotNone(channel)
        itunes_complete = channel.find(
            "itunes:complete",
            namespaces=self.xml_namespaces,
        )
        if self.podcast.itunes_complete:
            self.assertIsNotNone(itunes_complete)
            self.assertEqual(itunes_complete.text, "Yes")
        else:
            self.assertIsNone(itunes_complete)

    @skip_if_invalid_rss_xml
    def test_itunes_categories(self):
        channel = self.etree.find("channel")
        self.assertIsNotNone(channel)
        expected_categories = [
            self.podcast.itunes_primary_category,
            self.podcast.itunes_secondary_category,
        ]
        expected_categories = [c for c in expected_categories if c is not None]
        categories = channel.findall(
            "itunes:category",
            namespaces=self.xml_namespaces,
        )
        self.assertEqual(len(expected_categories), len(categories))
        expected_category_data = [
            (c.description, c.subcategory_description) for c in expected_categories
        ]
        actual_category_data = []
        for category in categories:
            description = (
                category.attrib["text"]
            )
            sub_description = ""
            children = category.getchildren()
            if children:
                self.assertEqual(len(children), 1)
                sub_description = children[0].attrib["text"]
            actual_category_data.append(
                (description, sub_description)
            )
        for expected in expected_category_data:
            self.assertIn(expected, actual_category_data)

    @skip_if_invalid_rss_xml
    def test_itunes_owner(self):
        channel = self.etree.find("channel")
        self.assertIsNotNone(channel)
        itunes_owner = channel.find(
            "itunes:owner",
            namespaces=self.xml_namespaces,
        )
        if self.podcast.itunes_owner:
            self.assertIsNotNone(itunes_owner)
            itunes_owner_name = itunes_owner.find(
                "itunes:name",
                namespaces=self.xml_namespaces,
            )
            self.assertEqual(itunes_owner_name.text, self.podcast.itunes_owner.name)
            itunes_owner_email = itunes_owner.find(
                "itunes:email",
                namespaces=self.xml_namespaces,
            )
            self.assertEqual(itunes_owner_email.text, self.podcast.itunes_owner.email)
        else:
            self.assertIsNone(itunes_owner)

    @skip_if_invalid_rss_xml
    def test_items(self):
        channel = self.etree.find("channel")
        self.assertIsNotNone(channel)
        self.assertEqual(
            self.podcast.episodes.count(),
            len(channel.findall("item"))
        )

    @skip_if_invalid_rss_xml
    def test_item_titles(self):
        channel = self.etree.find("channel")
        self.assertIsNotNone(channel)
        for episode in self.podcast.episodes.all():
            item = channel.find(f"item[guid='{episode.guid}']")
            self.assertIsNotNone(item)
            self.assertEqual(
                item.find("title").text,
                episode.title,
            )

    @skip_if_invalid_rss_xml
    def test_item_enclosure(self):
        channel = self.etree.find("channel")
        self.assertIsNotNone(channel)
        for episode in self.podcast.episodes.all():
            item = channel.find(f"item[guid='{episode.guid}']")
            enclosure = item.find("enclosure")
            self.assertIsNotNone(enclosure)
            expected_enclosure = {
                "length": str(episode.enclosure.length),
                "type": episode.enclosure.type,
                "url": episode.enclosure.url,
            }
            self.assertEqual(expected_enclosure, enclosure.attrib)

    @skip_if_invalid_rss_xml
    def test_item_chapters_count(self):
        channel = self.etree.find("channel")
        self.assertIsNotNone(channel)
        for episode in self.podcast.episodes.all():
            item = channel.find(f"item[guid='{episode.guid}']")
            expected_chapters = episode.chapters.all()
            chapter_group = item.find(
                "psc:chapters",
                namespaces=self.xml_namespaces,
            )
            if expected_chapters:
                self.assertIsNotNone(chapter_group)
                chapters = chapter_group.findall(
                    "psc:chapter",
                    namespaces=self.xml_namespaces,
                )
                self.assertEqual(
                    len(chapters),
                    expected_chapters.count(),
                )
            else:
                self.assertIsNone(chapter_group)
