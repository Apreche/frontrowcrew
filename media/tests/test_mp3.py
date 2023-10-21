import os
import tempfile
import unittest

from django import test

from frontrowcrew.tests import utils
from media import factories


@test.override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "frc_test_media"),
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "MP3Test",
        }
    },
)
class MP3Test(utils.FRCTestCase):

    def test_get_xmp_chapters(self):
        mp3 = factories.MP3Factory()
        expected_chapters = [
            {
                "title": "Marker 01",
                "start_time": 2382,
            }
        ]
        chapters = mp3.get_xmp_chapters()
        self.assertEqual(chapters, expected_chapters)

    def test_get_id3(self):
        mp3 = factories.MP3Factory()
        id3 = mp3.get_id3()
        test_frames = {
            "TCON": ["Blues"],
        }
        for key, value in test_frames.items():
            self.assertIn(key, id3)
            self.assertEqual(id3[key].text, value)

    def test_set_id3(self):
        mp3 = factories.MP3Factory()
        test_title = "GeekNights Podcast"
        test_performer = "Rym & Scott"
        detail_url = "https://frontrowcrew..com/foo/"
        mp3.set_id3(
            title=test_title,
            performer=test_performer,
            detail_url=detail_url,
        )
        id3 = mp3.get_id3()
        test_frames = {
            "TIT2": [test_title],
            "TPE1": [test_performer],
            "TCON": ["Podcast"],
        }
        for key, value in test_frames.items():
            self.assertIn(key, id3)
            self.assertEqual(id3[key].text, value)
        self.assertEqual(id3["WOAF"].url, detail_url)

    @unittest.skip("album images set from FileFields now")
    def test_set_id3_album_image_path(self):
        mp3 = factories.MP3Factory()
        album_image_path = os.path.join(
            os.path.dirname(__file__),
            "data/TestImage.png"
        )
        test_album_image_description = "test album cover"
        mp3.set_id3(
            album_image=album_image_path,
            album_image_description=test_album_image_description,
        )
        id3 = mp3.get_id3()
        apics = id3.getall("APIC")
        self.assertEqual(len(apics), 1)
        apic = apics[0]
        self.assertEqual(apic.mime, "image/png")
        self.assertEqual(apic.desc, test_album_image_description)

    @unittest.skip("album images set from FileFields now")
    def test_set_id3_album_image_fp(self):
        mp3 = factories.MP3Factory()
        album_image_path = os.path.join(
            os.path.dirname(__file__),
            "data/TestImage.png"
        )
        test_album_image_description = "test album cover"
        with open(album_image_path, "rb") as album_image_file:
            mp3.set_id3(
                album_image=album_image_file,
                album_image_description=test_album_image_description,
            )
        id3 = mp3.get_id3()
        apics = id3.getall("APIC")
        self.assertEqual(len(apics), 1)
        apic = apics[0]
        self.assertEqual(apic.mime, "image/png")
        self.assertEqual(apic.desc, test_album_image_description)

    def test_set_id3_basic_chapters(self):
        test_chapters = [
            {
                "name": "First Chapter",
                "start_time": 0,
                "end_time": 1000,
            },
            {
                "name": "Second Chapter",
                "start_time": 1000,
                "end_time": 2000,
            }
        ]
        mp3 = factories.MP3Factory()
        mp3.set_id3(
            chapters=test_chapters
        )
        id3 = mp3.get_id3()
        ctocs = id3.getall("CTOC")
        self.assertEqual(len(ctocs), 1)
        ctoc = ctocs[0]
        self.assertEqual(
            len(ctoc.child_element_ids),
            len(test_chapters),
        )

        chaps = id3.getall("CHAP")
        self.assertEqual(
            len(chaps), len(test_chapters),
        )
        for idx, test_chapter in enumerate(test_chapters):
            chap = chaps[idx]
            self.assertEqual(test_chapter["start_time"], chap.start_time)
            self.assertEqual(test_chapter["end_time"], chap.end_time)
            chap_sub_frames = chap.sub_frames
            chap_tit2 = chap_sub_frames.getall("TIT2")
            self.assertEqual(len(chap_tit2), 1)
            self.assertEqual(
                chap_tit2[0].text, [test_chapter["name"]]
            )

    def test_set_id3_advanced_chapters(self):
        chapter_image_path = os.path.join(
            os.path.dirname(__file__),
            "data/TestImage.png"
        )
        test_chapter_image_description = "test chapter image"
        with open(chapter_image_path, "rb") as test_chapter_image_file:
            test_file_field = type("",(object,),{"file": test_chapter_image_file})()
            test_chapters = [
                {
                    "name": "First Chapter",
                    "description": "First Chapter Description",
                    "url": "http://frontrowcrew.com",
                    "url_description": "Front Row Crew",
                    "start_time": 0,
                    "end_time": 1000,
                },
                {
                    "name": "Second Chapter",
                    "description": "Second Chapter Description",
                    "url": "http://frontrowcrew.com/asdf/",
                    "start_time": 1000,
                    "end_time": 2000,
                    "image": test_file_field,
                    "image_description": test_chapter_image_description,
                },
                {
                    "name": "Third Chapter",
                    "description": "Third Chapter Description",
                    "url_description": "asdf",
                    "start_time": 4000,
                    "end_time": 4100,
                    "image_description": "asdf",
                },
                {
                    "name": "Fourth Chapter",
                    "description": "Fourth Chapter Description",
                    "start_time": 5000,
                    "end_time": 5001,
                    "image": test_file_field,
                }
            ]
            mp3 = factories.MP3Factory()
            mp3.set_id3(
                chapters=test_chapters
            )
            id3 = mp3.get_id3()
            ctocs = id3.getall("CTOC")
            self.assertEqual(len(ctocs), 1)
            ctoc = ctocs[0]
            self.assertEqual(
                len(ctoc.child_element_ids),
                len(test_chapters),
            )

            chaps = id3.getall("CHAP")
            self.assertEqual(
                len(chaps), len(test_chapters),
            )
            chaps.sort(key=lambda x: x.element_id)
            for idx, test_chapter in enumerate(test_chapters):
                chap = chaps[idx]
                self.assertEqual(test_chapter["start_time"], chap.start_time)
                self.assertEqual(test_chapter["end_time"], chap.end_time)
                chap_sub_frames = chap.sub_frames
                chap_tit2s = chap_sub_frames.getall("TIT2")
                self.assertEqual(len(chap_tit2s), 1)
                chap_tit2 = chap_tit2s[0]
                self.assertEqual(
                    chap_tit2.text, [test_chapter["name"]]
                )
                chap_tit3s = chap_sub_frames.getall("TIT3")
                self.assertEqual(len(chap_tit3s), 1)
                chap_tit3 = chap_tit3s[0]
                self.assertEqual(
                    chap_tit3.text, [test_chapter["description"]]
                )
                chap_wxxxs = chap_sub_frames.getall("WXXX")
                if test_chapter.get("url", None) is not None:
                    self.assertEqual(len(chap_wxxxs), 1)
                    chap_wxxx = chap_wxxxs[0]
                    self.assertEqual(
                        chap_wxxx.url, test_chapter["url"]
                    )
                    self.assertEqual(
                        chap_wxxx.desc, test_chapter.get("url_description", "")
                    )
                else:
                    self.assertEqual(len(chap_wxxxs), 0)

                chap_apics = chap_sub_frames.getall("APIC")
                if test_chapter.get("image"):
                    self.assertEqual(len(chap_apics), 1)
                    chap_apic = chap_apics[0]
                    self.assertEqual(chap_apic.mime, "image/png")
                    self.assertEqual(
                        chap_apic.desc,
                        test_chapter.get("image_description", "")
                    )
                else:
                    self.assertEqual(len(chap_apics), 0)
