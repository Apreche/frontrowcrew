import os
import tempfile

from http import HTTPStatus
from xml import etree

from django import test, urls

from frontrowcrew.tests import utils

from shows import factories, models


@test.override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "frc_test_media"),
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "TotDFeedTest",
        }
    },
)
class TotDFeedTests(utils.FRCTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.xml_namespaces = {
            "dc": "http://purl.org/dc/elements/1.1/",
        }

    def test_totd_feed_404(self):
        """ 404 with no items? """
        url = urls.reverse("totd-rss")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_totd_feed_ok(self):
        """ Make sure the feed view loads """
        factories.RelatedLinkFactory(
            type_id=models.RelatedLinkType.THING_OF_THE_DAY,
            published=True,
        )
        url = urls.reverse("totd-rss")

        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_totd_feed_item_count(self):
        """ Make sure the feed has the correct published links """
        NUM_LINKS = 5
        factories.RelatedLinkFactory.create_batch(
            size=NUM_LINKS,
            type_id=models.RelatedLinkType.THING_OF_THE_DAY,
            published=True,
        )
        factories.RelatedLinkFactory.create_batch(
            size=NUM_LINKS + 1,
            type_id=models.RelatedLinkType.THING_OF_THE_DAY,
            unpublished=True,
        )
        factories.RelatedLinkFactory.create_batch(
            size=NUM_LINKS + 1,
            type_id=models.RelatedLinkType.FORUM_THREAD,
            published=True,
        )
        url = urls.reverse("totd-rss")

        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        items_etree = etree.ElementTree.fromstring(response.content)
        channel = items_etree.find("channel")
        self.assertIsNotNone(channel)
        items = channel.findall("item")
        self.assertEqual(len(items), NUM_LINKS)

    def test_totd_feed_item_contents(self):
        """ Make sure the feed has the correct published links """
        related_link = factories.RelatedLinkFactory(
            type_id=models.RelatedLinkType.THING_OF_THE_DAY,
            has_description=True,
            published=True,
        )
        url = urls.reverse("totd-rss")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        items_etree = etree.ElementTree.fromstring(response.content)
        channel = items_etree.find("channel")
        self.assertIsNotNone(channel)
        items = channel.findall("item")
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(
            item.find("title").text, related_link.title
        )
        self.assertEqual(
            item.find("description").text, related_link.description
        )
        self.assertEqual(
            item.find("link").text, related_link.url
        )
        self.assertEqual(
            item.find(
                "dc:creator",
                namespaces=self.xml_namespaces,
            ).text, related_link.author
        )
