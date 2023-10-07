import http
import os
import random
import tempfile

from django import test
from django import urls
from django.contrib.auth import models as auth_models
from mutagen.mp3 import MP3 as mutagen_mp3
from unittest import mock

from frontrowcrew.tests import utils
from creator import models as creator_models
from creator import views as creator_views
from media import factories as media_factories
from podcasts import factories as podcast_factories
from podcasts import models as podcast_models
from shows import factories as show_factories
from shows import models as show_models


@test.override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "frc_test_media"),
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "CreateTest",
        }
    },
)
class CreateTest(utils.FRCTestCase):

    def setUp(self):
        super().setUp()
        self.user = auth_models.User.objects.create_user(
            username="Test User",
            is_staff=True,
        )
        self.client = test.Client()
        self.client.force_login(user=self.user)

    def test_create_podcast_episode_get(self):
        """ Test getting the blank podcast episode creation form """
        mp3 = media_factories.MP3Factory()
        url = urls.reverse(
            "creator-podcast-episode",
            args=[mp3.id],
        )
        response = self.client.get(path=url)
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.OK,
        )

    @mock.patch("ftplib.FTP", autospec=True)
    def test_create_podcast_episode_post(self, mock_ftp):
        """ Test actual podcast episode creation """
        mp3 = media_factories.MP3Factory()
        url = urls.reverse(
            "creator-podcast-episode",
            args=[mp3.id],
        )

        test_data_dir_path = os.path.join(os.path.dirname(__file__), "data")
        test_image_name = "test_image.png"
        test_image_path = os.path.join(test_data_dir_path, test_image_name)
        destination = media_factories.FTPDestinationFactory()
        show = show_factories.ShowFactory(
            is_podcast=True,
        )
        content = show_factories.ContentFactory.build(
            show=show,
            is_markdown=True,
            is_podcast=True,
        )
        podcast_episode = content.podcast_episode
        main_form = {
            "destination": destination.id,
            "show": show.id,
            "catalog_number": content.pub_time.strftime("%Y%m%d"),
            "pub_time": content.pub_time.strftime("%Y-%m-%dT%H:%M"),
            "title": content.title,
            "tags": "taga, tagb",
            "body": content.original_content,
            "description": podcast_episode.description or "",
            "author_name": podcast_episode.author_name or "",
            "author_email": podcast_episode.author_email or "",
            "image_description": podcast_episode.image_description or "",
            "itunes_title": podcast_episode.itunes_title or "",
            "itunes_episode_number": podcast_episode.itunes_episode_number or "",
            "itunes_season_number": podcast_episode.itunes_season_number or "",
            "itunes_explicit": podcast_episode.itunes_explicit or "",
            "itunes_episode_type": podcast_episode.itunes_episode_type or "",
            "itunes_block": podcast_episode.itunes_block or "",
        }

        if random.randint(0, 1):
            test_image = open(test_image_path, "rb")
            main_form["image"] = test_image

        if random.randint(0, 1):
            test_itunes_image = open(test_image_path, "rb")
            main_form["itunes_image"] = test_itunes_image

        num_related_links = random.randint(0, 4)
        related_links = show_factories.RelatedLinkFactory.build_batch(size=num_related_links)
        related_link_forms = []
        for related_link in related_links:
            related_link_forms.append(
                {
                    "title": related_link.title,
                    "url": related_link.url,
                    "author": related_link.author,
                    "description": related_link.description or "",
                }
            )

        num_chapters = random.randint(0, 6)
        chapter_forms = []
        for chapter in podcast_factories.PodcastChapterFactory.build_batch(size=num_chapters):
            chapter_data = {
                "start_time": chapter.start_time,
                "title": chapter.title,
                "description": chapter.description or "",
                "url": chapter.url or "",
                "url_description": chapter.url_description or "",
                "image_description": chapter.image_description or "",
            }
            if random.randint(0, 1):
                test_image = open(test_image_path, "rb")
                chapter_data["image"] = test_image
            chapter_forms.append(chapter_data)
        payload = {}
        for key, value in main_form.items():
            payload[f"{creator_views.MAIN_FORM_PREFIX}-{key}"] = value
        for index, chapter_form in enumerate(chapter_forms):
            for key, value in chapter_form.items():
                payload[f"{creator_views.CHAPTER_FORMSET_PREFIX}-{index}-{key}"] = value
        for index, related_link_form in enumerate(related_link_forms):
            for key, value in related_link_form.items():
                payload[f"{creator_views.RELATED_LINK_FORMSET_PREFIX}-{index}-{key}"] = value
        formset_fields = ["TOTAL_FORMS", "INITIAL_FORMS", "MIN_NUM_FORMS", "MAX_NUM_FORMS"]
        for fieldname in formset_fields:
            payload[f"{creator_views.RELATED_LINK_FORMSET_PREFIX}-{fieldname}"] = len(related_link_forms)
            payload[f"{creator_views.CHAPTER_FORMSET_PREFIX}-{fieldname}"] = len(chapter_forms)

        response = self.client.post(
            path=url,
            data=payload,
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.CREATED,
        )

        # Verify created chapters are in database
        episode = response.context.get("episode", None)
        self.assertIsNotNone(episode)
        related_link_count = creator_models.RelatedLink.objects.filter(episode=episode).count()
        self.assertEqual(related_link_count, num_related_links)
        chapter_count = creator_models.Chapter.objects.filter(episode=episode).count()
        self.assertEqual(chapter_count, num_chapters)

        # Verify FTP happened correctly
        ftp_kwargs = {
            "host": destination.host,
        }
        for field, kwarg in [
            ("username", "user"),
            ("password", "passwd"),
            ("custom_timeout", "timeout"),
        ]:
            value = getattr(destination, field, None)
            if value:
                ftp_kwargs[kwarg] = value
        mock_ftp.assert_called_once_with(**ftp_kwargs)
        mock_ftp_connection = mock_ftp.return_value
        call_count = 2
        if destination.directory:
            call_count += 1
            mock_ftp_connection.cwd.assert_called_once_with(
                destination.directory
            )
        mp3.refresh_from_db()
        mock_ftp_connection.storbinary.assert_called_once_with(
            f"STOR {episode.catalog_number}.mp3", mp3.file
        )
        mock_ftp_connection.quit.assert_called_once()
        self.assertEqual(
            len(mock_ftp_connection.method_calls),
            call_count
        )

        # Verify all content created correctly
        contents = show_models.Content.objects.all()
        self.assertEqual(len(contents), 1)
        content = contents.first()
        content_properties = {
            "title": episode.title,
            "show": episode.show,
            "catalog_number": episode.catalog_number,
            "original_content": episode.body,
        }
        for field, value in content_properties.items():
            self.assertEqual(
                getattr(content, field), value
            )
        podcast_episode = content.podcast_episode
        podcast_episode_properties = {
            "podcast": episode.show.podcast,
            "title": episode.title,
            "description": episode.description,
            "author_name": episode.author_name,
            "author_email": episode.author_email,
            "image_description": episode.image_description,
            "itunes_explicit": episode.itunes_explicit,
            "itunes_title": episode.itunes_title,
            "itunes_episode_number": episode.itunes_episode_number,
            "itunes_season_number": episode.itunes_season_number,
        }
        for field, value in podcast_episode_properties.items():
            self.assertEqual(
                getattr(podcast_episode, field), value
            )
        if podcast_episode.image:
            self.assertEqual(podcast_episode.image, episode.image)
        else:
            self.assertFalse(episode.image)
        if podcast_episode.itunes_image:
            self.assertEqual(podcast_episode.itunes_image, episode.itunes_image)
        else:
            self.assertFalse(episode.itunes_image)

        self.assertEqual(
            episode.chapters.all().count(),
            podcast_episode.chapters.all().count(),
        )
        for original_chapter in episode.chapters.all():
            chapter = podcast_models.PodcastChapter.objects.get(
                episode=podcast_episode,
                start_time=original_chapter.start_time,
                title=original_chapter.title,
                description=original_chapter.description,
                url=original_chapter.url,
                url_description=original_chapter.url_description,
                image=original_chapter.image,
                image_description=original_chapter.image_description,
            )
            self.assertTrue(chapter)

        chapter_times = podcast_episode.chapters.all().order_by(
            "start_time"
        ).values_list("start_time", "end_time")
        for index in range(0, len(chapter_times) - 2):
            _, end = chapter_times[index]
            next_start, _ = chapter_times[index + 1]
            self.assertEqual(end + 1, next_start)

        self.assertEqual(
            episode.related_links.all().count(),
            content.related_links.all().count(),
        )
        for original_related_link in episode.related_links.all():
            related_link = show_models.RelatedLink.objects.get(
                content=content,
                type_id=show_models.RelatedLinkType.THING_OF_THE_DAY,
                title=original_related_link.title,
                description=original_related_link.description,
                url=original_related_link.url,
                author=original_related_link.author,
            )
            self.assertTrue(related_link)

        mp3_data = mutagen_mp3(mp3.file)
        # Only check one ID3 tag because it's too much to check all
        # We also have separate tests for ID3 functionality
        # We just want to make sure the ID3 was changed at all
        self.assertEqual(str(mp3_data.get("TIT2")), episode.title)

        # close test files
        main_itunes_image = main_form.get("itunes_image", None)
        if main_itunes_image:
            main_itunes_image.close()
        for chapter_form in chapter_forms:
            image = chapter_form.get("Image", None)
            if image is not None:
                image.close()
