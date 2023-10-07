import datetime
import dateutil.parser
import os
import tempfile

from mutagen import mp3 as mutagen_mp3
from django import test, urls
from django import utils as django_utils

from frontrowcrew import utils as frc_utils
from frontrowcrew.tests import utils
from creator import factories
from creator import tasks


@test.override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "frc_test_media"),
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "CreatorTaskTest",
        }
    },
)
class CreatorTaskTest(utils.FRCTestCase):

    def test_sort_chapters(self):
        episode = factories.EpisodeFactory(
            chapters=None, processed=False
        )
        c1 = factories.ChapterFactory(
            episode=episode,
            start_time=1,
        )
        c2 = factories.ChapterFactory(
            episode=episode,
            start_time=5,
        )
        c3 = factories.ChapterFactory(
            episode=episode,
            start_time=20,
            end_time=30
        )
        tasks.sort_chapters.apply(args=[episode.id])
        c1.refresh_from_db()
        self.assertEqual(c1.end_time, 4)
        c2.refresh_from_db()
        self.assertEqual(c2.end_time, 19)
        c3.refresh_from_db()
        self.assertEqual(c3.end_time, 30)

    def test_apply_id3_tags(self):
        episode = factories.EpisodeFactory(processed=False)
        tasks.apply_id3_tags.apply(args=[episode.id])
        episode.refresh_from_db()
        show = episode.show
        podcast = show.podcast
        mp3 = mutagen_mp3.MP3(episode.mp3.file)
        default_feed_url = urls.reverse(
            "show-podcast-rss",
            args=[show.slug]
        )
        detail_url = urls.reverse(
            "content-detail",
            args=[
                show.slug,
                episode.catalog_number,
                django_utils.text.slugify(episode.title)
            ]
        )
        required_assertions = {
            "TIT2": episode.title,
            "TALB": podcast.title,
            "TCON": "Podcast",
            "WFED": podcast.custom_public_feed_url or default_feed_url,
            "WOAF": detail_url,
        }
        for key, value in required_assertions.items():
            self.assertEqual(str(mp3.get(key)), value)

        optional_assertions = {
            "TPE1": podcast.itunes_author,
            "TCOP": podcast.copyright,
            "TDES": episode.description,
            "WCOP": podcast.creative_commons_license,
        }
        for key, value in optional_assertions.items():
            if value:
                self.assertEqual(str(mp3.get(key)), value)
            else:
                self.assertNotIn(key, mp3)

        # WOAR Check
        woar_url = frc_utils.sites.default_base_url()
        woar_key = f"WOAR:{woar_url}"
        self.assertIn(woar_key, mp3)

        # Datetime tag check
        datetime_tags = ["TDTG", "TDRL"]
        for tag in datetime_tags:
            raw_value = str(mp3.get(tag).text[0])
            date_value = dateutil.parser.parse(raw_value)
            self.assertIsInstance(
                date_value, datetime.datetime
            )

        # Chapter check
        chapters = episode.chapters.all().order_by("start_time")
        chapter_toc = mp3.get("CTOC:toc", None)
        if not chapters:
            self.assertIsNone(chapter_toc)
            self.assertFalse(
                any([tag.startswith("CHAP") for tag in mp3.keys()])
            )
        else:
            toc_elements = getattr(
                chapter_toc,
                "child_element_ids"
            )
            self.assertEqual(
                chapters.count(),
                len(toc_elements)
            )
            for idx, chapter in enumerate(
                chapters.order_by("start_time")
            ):
                chapname = f"ch{idx:02}"
                self.assertIn(chapname, toc_elements)
                chapter_tag = mp3.get(f"CHAP:{chapname}", {})
                sub_frames = chapter_tag.sub_frames
                self.assertEqual(
                    chapter.title,
                    str(sub_frames["TIT2"])
                )
                self.assertEqual(
                    chapter.start_time,
                    chapter_tag.start_time,
                )
                chapter_url = getattr(chapter, "url", None)
                if chapter_url:
                    chapter_url_desc = getattr(chapter, "url_description", "")
                    chapter_wxxx_key = f"WXXX:{chapter_url_desc}"
                    chapter_wxxx_frame = sub_frames.get(chapter_wxxx_key, None)
                    self.assertIsNotNone(chapter_wxxx_frame)
                    self.assertEqual(chapter_wxxx_frame.url, chapter_url)
                    self.assertEqual(chapter_wxxx_frame.desc, chapter_url_desc)
                else:
                    self.assertFalse(
                        any([tag.startswith("WXXX") for tag in sub_frames.keys()])
                    )
