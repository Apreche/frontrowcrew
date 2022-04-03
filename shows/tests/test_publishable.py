import datetime

from django.utils import timezone
from betafrontrowcrew.tests import utils

from shows import factories, models


class PublishableShowTests(utils.FRCTestCase):
    def setUp(self):
        super().setUp()
        self.now = timezone.now()
        one_day = datetime.timedelta(days=1)
        self.yesterday = self.now - one_day
        self.tomorrow = self.now + one_day

    def test_show_is_published(self):
        show = factories.ShowFactory(
            is_published=True,
            pub_time=self.yesterday,
        )
        all_shows = models.Show.objects.all()
        self.assertIn(show, all_shows)
        self.assertTrue(show.is_live)
        published_shows = models.Show.published.all()
        self.assertIn(show, published_shows)

    def test_show_not_published_flag(self):
        show = factories.ShowFactory(
            is_published=False,
            pub_time=self.yesterday,
        )
        all_shows = models.Show.objects.all()
        self.assertIn(show, all_shows)
        self.assertFalse(show.is_live)
        published_shows = models.Show.published.all()
        self.assertNotIn(show, published_shows)

    def test_show_not_published_time(self):
        show = factories.ShowFactory(
            is_published=True,
            pub_time=self.tomorrow,
        )
        all_shows = models.Show.objects.all()
        self.assertIn(show, all_shows)
        self.assertFalse(show.is_live)
        published_shows = models.Show.published.all()
        self.assertNotIn(show, published_shows)

    def test_show_not_published_all(self):
        show = factories.ShowFactory(
            is_published=False,
            pub_time=self.tomorrow,
        )
        all_shows = models.Show.objects.all()
        self.assertIn(show, all_shows)
        self.assertFalse(show.is_live)
        published_shows = models.Show.published.all()
        self.assertNotIn(show, published_shows)


class PublishableContentTests(utils.FRCTestCase):
    def setUp(self):
        super().setUp()
        self.now = timezone.now()
        one_day = datetime.timedelta(days=1)
        self.yesterday = self.now - one_day
        self.tomorrow = self.now + one_day

    def test_content_is_published(self):
        content = factories.ContentFactory(
            show__is_published=True,
            show__pub_time=self.yesterday,
            is_published=True,
            pub_time=self.yesterday,
        )
        all_content = models.Content.objects.all()
        self.assertIn(content, all_content)
        self.assertTrue(content.is_live)
        published_content = models.Content.published.all()
        self.assertIn(content, published_content)

    def test_content_not_published_show(self):
        content = factories.ContentFactory(
            show__is_published=False,
            show__pub_time=self.yesterday,
            is_published=True,
            pub_time=self.yesterday,
        )
        all_content = models.Content.objects.all()
        self.assertIn(content, all_content)
        self.assertFalse(content.is_live)
        published_content = models.Content.published.all()
        self.assertNotIn(content, published_content)

    def test_content_not_published_flag(self):
        content = factories.ContentFactory(
            show__is_published=True,
            show__pub_time=self.yesterday,
            is_published=False,
            pub_time=self.yesterday,
        )
        all_content = models.Content.objects.all()
        self.assertIn(content, all_content)
        self.assertFalse(content.is_live)
        published_content = models.Content.published.all()
        self.assertNotIn(content, published_content)

    def test_content_not_published_time(self):
        content = factories.ContentFactory(
            show__is_published=True,
            show__pub_time=self.yesterday,
            is_published=True,
            pub_time=self.tomorrow,
        )
        all_content = models.Content.objects.all()
        self.assertIn(content, all_content)
        self.assertFalse(content.is_live)
        published_content = models.Content.published.all()
        self.assertNotIn(content, published_content)

    def test_content_not_published_all(self):
        content = factories.ContentFactory(
            show__is_published=False,
            show__pub_time=self.tomorrow,
            is_published=False,
            pub_time=self.tomorrow,
        )
        all_content = models.Content.objects.all()
        self.assertIn(content, all_content)
        self.assertFalse(content.is_live)
        published_content = models.Content.published.all()
        self.assertNotIn(content, published_content)
