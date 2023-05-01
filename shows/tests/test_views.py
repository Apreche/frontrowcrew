import datetime
import os
import tempfile
from http import HTTPStatus

from django import test, urls
from django.utils import timezone

from betafrontrowcrew.tests import utils
from shows import factories, models


@test.override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "betafrc_test_media"),
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "HomepageTest",
        }
    },
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
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "betafrc_test_media"),
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "DisplayInNavTest",
        }
    },
)
class DisplayInNavTests(utils.FRCTestCase):
    def setUp(self):
        super().setUp()
        self.client = test.Client()

    def test_nav_show_list(self):
        good_show = factories.ShowFactory.create(display_in_nav=True, is_published=True)
        bad_show = factories.ShowFactory.create(display_in_nav=False, is_published=True)
        url = urls.reverse("homepage")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        found_shows = response.context.get("nav_shows", None)
        self.assertIsNotNone(found_shows)

        if good_show not in found_shows:
            print(
                f"Good Show {good_show} not found\n"
                f"published: {good_show.is_published}\n"
                f"pub_time: {good_show.pub_time}\n"
                f"found shows: {found_shows}\n"
            )
        if bad_show in found_shows:
            print(
                f"Bad Show {good_show} found\n"
                f"published: {good_show.is_published}\n"
                f"pub_time: {good_show.pub_time}\n"
                f"found shows: {found_shows}\n"
            )
        self.assertIn(good_show, found_shows)
        self.assertNotIn(bad_show, found_shows)

    def test_nav_show_list_not_admin(self):
        factories.ShowFactory.create(display_in_nav=True, is_published=True)
        url = urls.reverse("admin:login")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn("nav_shows", response.context)


@test.override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "betafrc_test_media"),
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "ShowDetailTest",
        }
    },
)
class ShowDetailTests(utils.FRCTestCase):
    def setUp(self):
        super().setUp()
        self.client = test.Client()

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
        content = factories.ContentFactory(is_published=False, show__is_published=False)
        show = content.show
        url = urls.reverse("show-detail", args=(show.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_show_detail_published(self):
        # make published content on unpublished show
        content = factories.ContentFactory(is_published=True, show__is_published=False)
        show = content.show
        url = urls.reverse("show-detail", args=(show.slug,))
        # Unpublished show should be 404
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # publish the show
        show.is_published = True
        yesterday = timezone.now() - datetime.timedelta(days=1)
        show.pub_time = yesterday
        show.save()
        # published show should no longer be 404
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # published content should be in result
        self.assertIn("page", response.context)
        page = response.context.get("page")
        objects = page.object_list
        self.assertIn(content, objects)
        # unpublish the content
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        content.pub_time = tomorrow
        content.save()
        # unpublishec content should no longer be in result
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        page = response.context.get("page")
        objects = page.object_list
        self.assertNotIn(content, objects)

    def test_child_show_detail(self):
        """
        Child show content should appear on list page of immediate parent show
        """
        content = factories.ContentFactory(is_published=True, show__is_published=True)
        child_show = content.show
        show = factories.ShowFactory(is_published=True)
        child_show.parent_show = show
        child_show.save()
        url = urls.reverse("show-detail", args=(show.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("page", response.context)
        page = response.context.get("page")
        objects = page.object_list
        self.assertIn(content, objects)

    def test_show_detail_tagged(self):
        techanime_content = factories.ContentFactory(
            is_published=True, show__is_published=True, tags=["tech", "anime"]
        )
        show = techanime_content.show
        tech_content = factories.ContentFactory(
            is_published=True, show=show, tags=["tech"]
        )
        anime_content = factories.ContentFactory(
            is_published=True, show=show, tags=["anime"]
        )
        notag_content = factories.ContentFactory(
            is_published=True,
            show=show,
        )
        bikes_content = factories.ContentFactory(
            is_published=True, show=show, tags=["bikes"]
        )

        tag_checks = [
            ("tech", [techanime_content, tech_content]),
            ("anime", [techanime_content, anime_content]),
            ("bikes", [bikes_content]),
            ("tech+anime", [techanime_content]),
        ]
        for tags, contents in tag_checks:
            url = urls.reverse("show-tag-filter", args=(show.slug, tags))
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn("show", response.context)
            self.assertEqual(response.context["show"], show)
            tag_context = response.context.get("tags", "")
            for tag in tags.split("+"):
                self.assertIn(tag, tag_context)
            page = response.context.get("page")
            content_context = page.object_list
            self.assertNotIn(notag_content, content_context)
            self.assertEqual(len(contents), len(content_context))
            for content in contents:
                self.assertIn(content, content_context)


@test.override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "betafrc_test_media"),
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "ContentDetailTest",
        }
    },
)
class ContentDetailTests(utils.FRCTestCase):
    def setUp(self):
        super().setUp()
        self.client = test.Client()

    def test_content_detail(self):
        content = factories.ContentFactory(is_published=True, show__is_published=True)
        thing = factories.RelatedLinkFactory(
            content=content, type_id=models.RelatedLinkType.THING_OF_THE_DAY
        )
        url = urls.reverse(
            "content-detail",
            args=(
                content.show.slug,
                content.catalog_number,
                content.slug,
            ),
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("content", response.context)
        self.assertEqual(response.context["content"], content)
        things = response.context["content"].things_of_the_day
        self.assertIn(thing, things)

    def test_content_detail_404(self):
        content = factories.ContentFactory(is_published=False)
        url = urls.reverse(
            "content-detail",
            args=(
                content.show.slug,
                content.catalog_number + "1",
                content.slug,
            ),
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
            ),
        )
        url = urls.reverse(
            "content-detail-noslug",
            args=(
                content.show.slug,
                content.catalog_number,
            ),
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
            ),
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
            ),
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

    def test_content_detail_child_show(self):
        """
        Content visited with parent show URLs should redirect to the child-show
        """
        content = factories.ContentFactory(
            is_published=True,
            show__is_published=True,
        )
        child_show = content.show
        show = factories.ShowFactory(
            is_published=True,
        )
        child_show.parent_show = show
        child_show.save()
        url = urls.reverse(
            "content-detail",
            args=(
                child_show.slug,
                content.catalog_number,
                content.slug,
            ),
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        parent_url = urls.reverse(
            "content-detail",
            args=(
                show.slug,
                content.catalog_number,
                content.slug,
            ),
        )
        response = self.client.get(parent_url)
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)
        redirect_url = response.url
        response = self.client.get(redirect_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_thing_of_the_day_list_empty(self):
        url = urls.reverse("totd-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_thing_of_the_day_list(self):
        thing = factories.RelatedLinkFactory(
            type_id=models.RelatedLinkType.THING_OF_THE_DAY, published=True
        )
        url = urls.reverse("totd-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("things_of_the_day", response.context)
        thing_response = response.context["things_of_the_day"]
        self.assertEqual(len(thing_response), 1)
        self.assertIn(thing, thing_response)

    def test_similar_content(self):
        tech_anime_content = factories.ContentFactory(
            is_published=True,
            show__is_published=True,
            tags=["tech", "anime"],
        )
        tech_content = factories.ContentFactory(
            is_published=True,
            show__is_published=True,
            tags=["tech"],
        )
        foo_content = factories.ContentFactory(
            is_published=True,
            show__is_published=True,
            tags=["foo"],
        )
        notag_content = factories.ContentFactory(
            is_published=True,
            show__is_published=True,
        )

        # unpublished tech content that should not appear
        factories.ContentFactory(
            is_published=False,
            show__is_published=True,
            tags=["tech"],
        )
        test_cases = {
            tech_anime_content: [tech_content],
            tech_content: [tech_anime_content],
            foo_content: [],
            notag_content: [],
        }
        for content, similar_content in test_cases.items():
            url = urls.reverse(
                "content-detail",
                args=(
                    content.show.slug,
                    content.catalog_number,
                    content.slug,
                ),
            )
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertIn("similar_content", response.context)
            self.assertEqual(list(response.context["similar_content"]), similar_content)


@test.override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "betafrc_test_media"),
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "TagFilterTest",
        }
    },
)
class TagFilterTests(utils.FRCTestCase):
    def setUp(self):
        super().setUp()
        self.client = test.Client()

    def test_tag_filter(self):
        tag = "bikes"
        tagged_content = factories.ContentFactory(
            is_published=True, show__is_published=True, tags=[tag]
        )
        untagged_content = factories.ContentFactory(
            is_published=True,
            show__is_published=True,
        )
        url = urls.reverse("tag-filter", args=(tag,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("page", response.context)
        page = response.context.get("page")
        objects = page.object_list
        self.assertIn(tagged_content, objects)
        self.assertNotIn(untagged_content, objects)

    def test_tag_filter_multiple(self):
        techanime_content = factories.ContentFactory(
            is_published=True, show__is_published=True, tags=["tech", "anime"]
        )
        tech_content = factories.ContentFactory(
            is_published=True, show__is_published=True, tags=["tech"]
        )
        anime_content = factories.ContentFactory(
            is_published=True, show__is_published=True, tags=["anime"]
        )
        notag_content = factories.ContentFactory(
            is_published=True,
            show__is_published=True,
        )
        bikes_content = factories.ContentFactory(
            is_published=True, show__is_published=True, tags=["bikes"]
        )

        tag_checks = [
            ("tech", [techanime_content, tech_content]),
            ("anime", [techanime_content, anime_content]),
            ("bikes", [bikes_content]),
            ("tech+anime", [techanime_content]),
        ]
        for tags, contents in tag_checks:
            url = urls.reverse("tag-filter", args=(tags,))
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            tag_context = response.context.get("tags", "")
            for tag in tags.split("+"):
                self.assertIn(tag, tag_context)
            page = response.context.get("page")
            content_context = page.object_list
            self.assertNotIn(notag_content, content_context)
            self.assertEqual(len(contents), len(content_context))
            for content in contents:
                self.assertIn(content, content_context)
