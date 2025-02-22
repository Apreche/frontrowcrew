import os
import tempfile
from http import HTTPStatus
from xml import etree

from django import test, urls

from frontrowcrew.tests import utils
from podcasts.tests.utils import skip_if_invalid_rss_xml

from .. import factories


@test.override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "frc_test_media"),
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "ShowFeedTest",
        }
    },
)
class ShowFeedTests(utils.FRCTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.show = factories.ShowFactory(
            is_published=True,
        )
        cls.url = urls.reverse(
            "show-rss",
            kwargs={"show_slug": cls.show.slug},
        )

    def setUp(self):
        super().setUp()
        self.response = self.client.get(self.url)
        if self.response.status_code == HTTPStatus.OK:
            try:
                self.etree = etree.ElementTree.fromstring(self.response.content)
            except Exception as etree_exception:
                self.etree_exception = etree_exception

    def test_show_feed_ok(self):
        self.assertEqual(self.response.status_code, HTTPStatus.OK)

    def test_show_feed_404(self):
        url = urls.reverse(
            "show-rss",
            kwargs={"show_slug": f"{self.show.slug}x"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_etree_ok(self):
        if self.response.status_code != HTTPStatus.OK:
            self.skipTest("Skip because of failed request.")
        etree_exception = getattr(self, "etree_exception", None)
        self.assertIsNone(etree_exception)

    @skip_if_invalid_rss_xml
    def test_title(self):
        channel = self.etree.find("channel")
        title = channel.find("title")
        self.assertIsNotNone(title)
        self.assertEqual(title.text, self.show.title)

    @skip_if_invalid_rss_xml
    def test_items(self):
        factories.ContentFactory(show=self.show, is_published=True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        items_etree = etree.ElementTree.fromstring(response.content)
        channel = items_etree.find("channel")
        self.assertIsNotNone(channel)
        items = channel.findall("item")
        self.assertEqual(len(items), 1)

    @skip_if_invalid_rss_xml
    def test_child_show_items(self):
        """
        Verify that content from sub-shows appears in RSS feed
        """
        child_content = factories.ContentFactory(
            is_published=True,
            show__is_published=True,
        )
        child_show = child_content.show
        child_show.parent_show = self.show
        child_show.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        sub_etree = etree.ElementTree.fromstring(response.content)
        channel = sub_etree.find("channel")
        title = channel.find("title")
        self.assertIsNotNone(title)
        self.assertEqual(title.text, self.show.title)
        items = channel.findall("item")
        self.assertEqual(len(items), 1)
        title = items[0].find("title")
        self.assertIsNotNone(title)
        self.assertEqual(title.text, child_content.title)
