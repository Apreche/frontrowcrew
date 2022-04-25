import datetime

from http import HTTPStatus
from django import test, urls
from django.core.cache import cache
from django.utils import timezone
from betafrontrowcrew.tests import utils

from shows import factories


@test.override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'
)
class HomepageTests(utils.FRCTestCase):
    def setUp(self):
        super().setUp()
        self.client = test.Client()

    def test_homepage_ok(self):
        url = urls.reverse("homepage")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)


@test.override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'
)
class DisplayInNavTests(utils.FRCTestCase):
    def setUp(self):
        super().setUp()
        self.client = test.Client()
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_nav_show_list(self):
        good_show = factories.ShowFactory.create(display_in_nav=True, is_published=True)
        bad_show = factories.ShowFactory.create(display_in_nav=False, is_published=True)
        url = urls.reverse("homepage")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("nav_shows", response.context)
        self.assertIn(good_show, response.context["nav_shows"])
        self.assertNotIn(bad_show, response.context["nav_shows"])

    def test_nav_show_list_not_admin(self):
        factories.ShowFactory.create(display_in_nav=True, is_published=True)
        url = urls.reverse("admin:login")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn("nav_shows", response.context)


@test.override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage',
)
class ShowDetailTests(utils.FRCTestCase):
    def setUp(self):
        super().setUp()
        self.client = test.Client()
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_show_detail(self):
        content = factories.ContentFactory(is_published=True, show__is_published=True)
        show = content.show
        url = urls.reverse("show-detail", args=(show.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("show", response.context)
        self.assertEqual(response.context["show"], show)

    def test_show_detail_404_bad_url(self):
        content = factories.ContentFactory(is_published=True, show__is_published=True)
        show = content.show
        url = urls.reverse("show-detail", args=(show.slug + "WRONG",))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_show_detail_404_unpublished(self):
        content = factories.ContentFactory(is_published=False, show__is_published=True)
        show = content.show
        url = urls.reverse("show-detail", args=(show.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_show_detail_404_no_content(self):
        show = factories.ShowFactory(is_published=True)
        url = urls.reverse("show-detail", args=(show.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_show_detail_published(self):
        content = factories.ContentFactory(is_published=False)
        show = content.show
        url = urls.reverse(
            "show-detail",
            args=(show.slug,)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        content.is_published = True
        yesterday = timezone.now() - datetime.timedelta(days=1)
        content.pub_time = yesterday
        content.save()
        show.is_published = True
        show.pub_time = yesterday
        show.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("page", response.context)
        objects = response.context['page'].paginator.page(1).object_list
        self.assertIn(content, objects)
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        content.pub_time = tomorrow
        content.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_sub_show_detail(self):
        """
        Sub-show content should appear on list page of immediate parent show
        """
        content = factories.ContentFactory(is_published=True, show__is_published=True)
        sub_show = content.show
        show = factories.ShowFactory(is_published=True)
        show.sub_shows.add(sub_show)
        url = urls.reverse(
            "show-detail",
            args=(show.slug,)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("page", response.context)
        objects = response.context['page'].paginator.page(1).object_list
        self.assertIn(content, objects)


@test.override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'
)
class ContentDetailTests(utils.FRCTestCase):
    def setUp(self):
        super().setUp()
        self.client = test.Client()
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_content_detail(self):
        content = factories.ContentFactory(is_published=True, show__is_published=True)
        url = urls.reverse(
            "content-detail",
            args=(
                content.show.slug,
                content.catalog_number,
                content.slug,
            )
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("content", response.context)
        self.assertEqual(response.context["content"], content)

    def test_content_detail_404(self):
        content = factories.ContentFactory(is_published=False)
        url = urls.reverse(
            "content-detail",
            args=(
                content.show.slug,
                content.catalog_number + "1",
                content.slug,
            )
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_content_detail_redirects(self):
        """
        If slug is wrong or missing for content detail, it should redirect
        """
        content = factories.ContentFactory(is_published=True, show__is_published=True)
        correct_url = urls.reverse(
            "content-detail",
            args=(
                content.show.slug,
                content.catalog_number,
                content.slug,
            )
        )
        url = urls.reverse(
            "content-detail-noslug",
            args=(
                content.show.slug,
                content.catalog_number,
            )
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)
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
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)
        self.assertEqual(response.url, correct_url)

    def test_content_detail_published(self):
        content = factories.ContentFactory(
            is_published=False,
            show__is_published=False,
        )
        url = urls.reverse(
            "content-detail",
            args=(
                content.show.slug,
                content.catalog_number,
                content.slug,
            )
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        content.is_published = True
        content.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        yesterday = timezone.now() - datetime.timedelta(days=1)
        content.pub_time = yesterday
        content.save()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        show = content.show
        show.is_published = True
        show.pub_time = yesterday
        show.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content.is_published = False
        content.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_content_detail_subshow(self):
        """
        Content visited with parent show URLs should redirect to the sub-show
        """
        content = factories.ContentFactory(
            is_published=True,
            show__is_published=True,
        )
        sub_show = content.show
        show = factories.ShowFactory(
            is_published=True,
        )
        show.sub_shows.add(sub_show)
        url = urls.reverse(
            "content-detail",
            args=(
                sub_show.slug,
                content.catalog_number,
                content.slug,
            )
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        parent_url = urls.reverse(
            "content-detail",
            args=(
                show.slug,
                content.catalog_number,
                content.slug,
            )
        )
        response = self.client.get(parent_url)
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)
        redirect_url = response.url
        response = self.client.get(redirect_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)