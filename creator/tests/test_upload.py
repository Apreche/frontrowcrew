import http
import os
import tempfile

from django import test
from django import urls
from django.contrib.auth import models as auth_models
from betafrontrowcrew.tests import utils

from media import models as media_models


@test.override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "betafrc_test_media"),
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class UploadTest(utils.FRCTestCase):

    def setUp(self):
        super().setUp()
        self.user = auth_models.User.objects.create_user(
            username="Test User",
            is_staff=True,
        )
        self.client = test.Client()
        self.client.force_login(user=self.user)

    def test_upload_mp3_get(self):
        """ Test getting the blank mp3 upload form"""
        url = urls.reverse("creator-upload")
        response = self.client.get(path=url,)
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.OK,
        )

    def test_upload_mp3_post(self):
        """ Test posting to the MP3 upload form """
        test_data_dir_path = os.path.join(os.path.dirname(__file__), "data")
        test_file_name = "test_podcast.mp3"
        test_file_path = os.path.join(test_data_dir_path, test_file_name)
        url = urls.reverse("creator-upload")
        with open(test_file_path, "rb") as test_file:
            test_data = {"file": test_file}
            response = self.client.post(
                path=url,
                data=test_data,
                HTTP_ACCEPT="text/html"
            )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.FOUND,
        )
        mp3 = media_models.MP3.objects.latest()
        expected_redirect_url = urls.reverse(
            "creator-podcast-episode",
            args=[mp3.id],
        )
        self.assertEqual(
            response.url,
            expected_redirect_url,
        )

    def test_upload_mp3_post_json(self):
        """ Test posting to the MP3 upload form with json response """
        test_data_dir_path = os.path.join(os.path.dirname(__file__), "data")
        test_file_name = "test_podcast.mp3"
        test_file_path = os.path.join(test_data_dir_path, test_file_name)
        url = urls.reverse("creator-upload")
        with open(test_file_path, "rb") as test_file:
            test_data = {"file": test_file}
            response = self.client.post(
                path=url,
                data=test_data,
                HTTP_ACCEPT="application/json"
            )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.OK,
        )
        mp3 = media_models.MP3.objects.latest()
        expected_redirect_url = urls.reverse(
            "creator-podcast-episode",
            args=[mp3.id],
        )
        response_data = response.json()
        actual_response_url = response_data.get("redirect_url", None)
        self.assertEqual(
            actual_response_url,
            expected_redirect_url,
        )

    def test_upload_mp3_post_invalid(self):
        """ Test posting to the MP3 upload form """
        test_data_dir_path = os.path.join(os.path.dirname(__file__), "data")
        test_file_name = "test_text.txt"
        test_file_path = os.path.join(test_data_dir_path, test_file_name)
        url = urls.reverse("creator-upload")
        with open(test_file_path, "rb") as test_file:
            test_data = {"file": test_file}
            response = self.client.post(
                path=url,
                data=test_data,
            )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
        )
        self.assertIn(
            "Uploaded file is not an audio file with ID3",
            response.content.decode("utf-8")
        )
