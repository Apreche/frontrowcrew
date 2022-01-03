from django import test, urls
from django.utils import timezone

from betafrontrowcrew.tests import utils
from . import factories, models


class FactoryTests(utils.FRCTestCase):
    def test_show_factory(self):
        show = factories.ShowFactory.create()
        self.assertIsInstance(show, models.Show)

    def test_content_factory(self):
        content = factories.ContentFactory.create()
        self.assertIsInstance(content, models.Content)
        self.assertEqual(content.content_format, models.Content.Format.MARKDOWN)
        self.assertNotEqual(content.original_content, content.rendered_html)

    def test_content_factory_draft(self):
        content = factories.ContentFactory.create(draft=True)
        self.assertFalse(content.published)
        self.assertTrue(content.pub_time > timezone.now())

    def test_content_factory_legacy_html(self):
        content = factories.ContentFactory.create(legacy_html=True)
        self.assertEqual(content.content_format, models.Content.Format.HTML)
        self.assertEqual(content.original_content, content.rendered_html)


@test.override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'
)
class HomepageTests(utils.FRCTestCase):
    def setUp(self):
        super().setUp()
        self.client = test.Client()

    def test_homepage_ok(self):
        show = factories.ShowFactory()
        url = urls.reverse("homepage")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(show, response.context["shows"])


@test.override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage',
)
class ShowTests(utils.FRCTestCase):
    def setUp(self):
        super().setUp()
        self.client = test.Client()

    def test_show_detail(self):
        show = factories.ShowFactory()
        url = urls.reverse("show-detail", args=(show.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['show'], show)

    def test_show_detail_404(self):
        show = factories.ShowFactory()
        url = urls.reverse("show-detail", args=(show.slug + "WRONG",))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_content_detail(self):
        content = factories.ContentFactory()
        url = urls.reverse(
            "content-detail",
            args=(
                content.show.slug,
                content.catalog_number,
                content.slug,
            )
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['content'], content)

    def test_content_detail_404(self):
        content = factories.ContentFactory()
        url = urls.reverse(
            "content-detail",
            args=(
                content.show.slug,
                content.catalog_number + "1",
                content.slug,
            )
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_content_detail_redirects(self):
        content = factories.ContentFactory()
        correct_url = urls.reverse(
            "content-detail",
            args=(
                content.show.slug,
                content.catalog_number,
                content.slug,
            )
        )
        url = urls.reverse(
            "content-detail",
            args=(
                content.show.slug,
                content.catalog_number,
            )
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, correct_url)
        url = urls.reverse(
            "content-detail",
            args=(
                content.show.slug,
                content.catalog_number,
                content.slug + "wrong",
            )
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, correct_url)
