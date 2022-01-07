import datetime
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
        self.assertFalse(content.is_published)
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

    def test_show_detail_published(self):
        show = factories.ShowFactory(draft=True)
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

    def test_published_content_manager(self):
        content = factories.ContentFactory(draft=True)
        published_content = models.Content.published.all()
        self.assertNotIn(content, published_content)
        content.is_published = True
        content.save()
        published_content = models.Content.published.all()
        self.assertNotIn(content, published_content)
        yesterday = timezone.now() - datetime.timedelta(days=1)
        content.pub_time = yesterday
        content.save()
        published_content = models.Content.published.all()
        self.assertIn(content, published_content)
        content.is_published = False
        content.save()
        published_content = models.Content.published.all()
        self.assertNotIn(content, published_content)

    def test_content_detail_published(self):
        content = factories.ContentFactory(draft=True)
        url = urls.reverse(
            "content-detail",
            args=(
                content.show.slug,
                content.catalog_number,
                content.slug,
            )
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        content.is_published = True
        content.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        yesterday = timezone.now() - datetime.timedelta(days=1)
        content.pub_time = yesterday
        content.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content.is_published = False
        content.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_content_list_published(self):
        content = factories.ContentFactory(draft=True)
        url = urls.reverse(
            "show-detail",
            args=(
                content.show.slug,
            )
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        objects = response.context['page'].paginator.page(1).object_list
        self.assertNotIn(content, objects)
        content.is_published = True
        content.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        objects = response.context['page'].paginator.page(1).object_list
        self.assertNotIn(content, objects)
        yesterday = timezone.now() - datetime.timedelta(days=1)
        content.pub_time = yesterday
        content.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        objects = response.context['page'].paginator.page(1).object_list
        self.assertIn(content, objects)
        content.is_published = False
        content.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        objects = response.context['page'].paginator.page(1).object_list
        self.assertNotIn(content, objects)
