import os
import tempfile
from http import HTTPStatus

from django import test, urls
from django.utils import http

from frontrowcrew.tests import utils
from shows import factories


@test.override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "frc_test_media"),
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "SearchTest",
        }
    },
)
class SearchTests(utils.FRCTestCase):
    """
    Test the content full text search functionality
    It's hard to test it thoroughly so we just check for the basics
    """

    def setUp(self):
        super().setUp()
        self.client = test.Client()

    def test_no_query_content_search(self):
        """If there is no query the search results page should still load"""
        url = urls.reverse("content-search")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("page", response.context)
        page = response.context["page"]
        paginator = page.paginator
        self.assertEqual(paginator.num_pages, 1)
        self.assertEqual(paginator.count, 0)

    def test_content_search(self):
        """Test that only the matching content is in the results"""

        # This content will appear in the search result
        content = factories.ContentFactory(
            is_published=True,
            show__is_published=True,
            is_markdown=False,
            title="Hello",
            raw_content="<p>Hello</p>",
        )

        # These contents should not appear in the search results
        factories.ContentFactory(
            is_published=True,
            show__is_published=True,
            is_markdown=False,
            title="Goodbye",
            raw_content="<h1>Goodbye</h1>",
        )
        factories.ContentFactory(
            is_published=False,
            show__is_published=True,
            is_markdown=False,
            title="Hello",
            raw_content="<div>Hello</div>",
        )

        base_url = urls.reverse("content-search")
        params = http.urlencode({"q": "Hello"})
        url = f"{base_url}?{params}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("page", response.context)
        page = response.context["page"]
        paginator = page.paginator
        self.assertEqual(paginator.num_pages, 1)
        self.assertEqual(paginator.count, 1)
        results = page.object_list
        self.assertIn(content, results)

    def test_no_results_content_search(self):
        """Test the case where a query has no matches"""

        factories.ContentFactory(
            is_published=True,
            show__is_published=True,
            is_markdown=False,
            title="Hello",
            raw_content="<p>Hello</p>",
        )
        factories.ContentFactory(
            is_published=True,
            show__is_published=True,
            is_markdown=False,
            title="Goodbye",
            raw_content="<h1>Goodbye</h1>",
        )
        factories.ContentFactory(
            is_published=False,
            show__is_published=True,
            is_markdown=False,
            title="Hello",
            raw_content="<div>Hello</div>",
        )

        base_url = urls.reverse("content-search")
        params = http.urlencode({"q": "Hola"})
        url = f"{base_url}?{params}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("page", response.context)
        page = response.context["page"]
        paginator = page.paginator
        self.assertEqual(paginator.num_pages, 1)
        self.assertEqual(paginator.count, 0)

    def test_search_ranking(self):
        """Verify title matches rank higher than body matches"""

        top_content = factories.ContentFactory(
            is_published=True,
            show__is_published=True,
            is_markdown=False,
            title="Hello",
            raw_content="<p>Hello</p>",
        )
        middle_content = factories.ContentFactory(
            is_published=True,
            show__is_published=True,
            is_markdown=False,
            title="Hello",
            raw_content="<p>Goodbye</p>",
        )
        bottom_content = factories.ContentFactory(
            is_published=True,
            show__is_published=True,
            is_markdown=False,
            title="Goodbye",
            raw_content="<h1>Hello</h1>",
        )

        # Content that will not be in the result
        factories.ContentFactory(
            is_published=True,
            show__is_published=True,
            is_markdown=False,
            title="Goodbye",
            raw_content="<div>Goodbye</div>",
        )
        factories.ContentFactory(
            is_published=False,
            show__is_published=True,
            is_markdown=False,
            title="Hello",
            raw_content="<div>Hello</div>",
        )

        base_url = urls.reverse("content-search")
        params = http.urlencode({"q": "Hello"})
        url = f"{base_url}?{params}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("page", response.context)
        page = response.context["page"]
        paginator = page.paginator
        self.assertEqual(paginator.num_pages, 1)
        self.assertEqual(paginator.count, 3)
        results = page.object_list
        top_result, middle_result, bottom_result = results
        self.assertEqual(top_content, top_result)
        self.assertEqual(middle_content, middle_result)
        self.assertEqual(bottom_content, bottom_result)
