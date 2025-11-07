import csv
import os
import tempfile
from http import HTTPStatus

from django import test, urls
from django.conf import global_settings, settings

from etl import factories as etl_factories
from frontrowcrew.tests import utils
from shows import factories as show_factories


@test.override_settings(
    STORAGES=global_settings.STORAGES,
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "frc_test_media"),
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "HomepageTest",
        }
    },
)
class RedirectTests(utils.FRCTestCase):
    REDIRECT_TEST_FILE = "legacy_redirects/tests/data/redirect_tests.csv"

    def setUp(self):
        super().setUp()
        self.client = test.Client()
        self.show = show_factories.ShowFactory.create(
            title="geeknights",
            is_published=True,
            is_podcast=True,
        )
        self.content = show_factories.ContentFactory.create(
            show=self.show,
            is_published=True,
            is_podcast=True,
        )
        self.content.tags.add("board-games")
        self.content.tags.add("video-games")
        self.content.tags.add("anime")

    def test_most_redirects(self):
        """Test most of the redirects using test cases from a CSV"""
        test_file_path = os.path.join(
            settings.BASE_DIR,
            self.REDIRECT_TEST_FILE,
        )
        with open(test_file_path) as testfile:
            testreader = csv.reader(testfile, delimiter=",", quotechar='"')
            for from_url, to_url in testreader:
                response = self.client.get(from_url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.MOVED_PERMANENTLY,
                )
                self.assertEqual(response.url, to_url)

    def test_news_detail_redirect(self):
        """Test the news detail redirect"""
        show = show_factories.ShowFactory.create(
            title="news",
            is_published=True,
            is_podcast=True,
        )
        content = show_factories.ContentFactory.create(
            show=show,
            is_published=True,
            is_podcast=True,
        )
        import_record = etl_factories.ImportRecordFactory(
            old_table_name="news_news",
            new_id=content.id,
            new_table_name="shows_content",
        )
        url = urls.reverse(
            "legacy-redirect-news-detail-date-slug",
            kwargs={
                "year": content.pub_time.year,
                "month": content.pub_time.month,
                "day": content.pub_time.day,
                "slug": import_record.source_record["old_slug"],
            },
        )
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.MOVED_PERMANENTLY,
        )
        self.assertEqual(response.url, content.get_absolute_url())

    def test_episode_detail_redirect(self):
        """Test the episode detail redirect"""
        import_record = etl_factories.ImportRecordFactory(
            old_table_name="podcast_episode",
            new_id=self.content.id,
            new_table_name="shows_content",
        )
        self.content.refresh_from_db()
        redirect_patterns = [
            urls.reverse(
                "legacy-redirect-episode-detail-date-slug",
                kwargs={
                    "year": self.content.pub_time.year,
                    "month": self.content.pub_time.month,
                    "day": self.content.pub_time.day,
                    "slug": import_record.source_record["old_slug"],
                },
            ),
            urls.reverse(
                "legacy-redirect-episode-detail-date",
                kwargs={
                    "year": self.content.pub_time.year,
                    "month": self.content.pub_time.month,
                    "day": self.content.pub_time.day,
                },
            ),
            urls.reverse(
                "legacy-redirect-episode-detail-date-geeknights-slug",
                kwargs={
                    "year": self.content.pub_time.year,
                    "month": self.content.pub_time.month,
                    "day": self.content.pub_time.day,
                    "slug": import_record.source_record["old_slug"],
                },
            ),
            urls.reverse(
                "legacy-redirect-episodes-detail-date-slug",
                kwargs={
                    "year": self.content.pub_time.year,
                    "month": self.content.pub_time.month,
                    "day": self.content.pub_time.day,
                    "slug": import_record.source_record["old_slug"],
                },
            ),
            urls.reverse(
                "legacy-redirect-episodes-detail-date",
                kwargs={
                    "year": self.content.pub_time.year,
                    "month": self.content.pub_time.month,
                    "day": self.content.pub_time.day,
                },
            ),
        ]
        result_url = self.content.get_absolute_url()
        for url in redirect_patterns:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                HTTPStatus.MOVED_PERMANENTLY,
            )
            self.assertEqual(response.url, result_url)
