import os
import tempfile
from unittest import mock

from django import test

from frontrowcrew.tests import utils
from media import factories


@test.override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "frc_test_media"),
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "FTPDestinationTest",
        }
    },
)
class FTPDestinationTest(utils.FRCTestCase):
    @mock.patch("ftplib.FTP", autospec=True)
    def test_upload(self, mock_ftp):
        destination = factories.FTPDestinationFactory()
        mp3 = factories.MP3Factory()
        filename = os.path.basename(mp3.file.name)
        url = destination.upload(mp3.file, filename)
        self.assertEqual(url, f"{destination.url_prefix}{filename}")
        kwargs = {
            "host": destination.host,
        }
        for field, kwarg in [
            ("username", "user"),
            ("password", "passwd"),
            ("custom_timeout", "timeout"),
        ]:
            value = getattr(destination, field, None)
            if value:
                kwargs[kwarg] = value
        mock_ftp.assert_called_once_with(**kwargs)
        mock_ftp_connection = mock_ftp.return_value
        call_count = 2
        if destination.directory:
            call_count += 1
            mock_ftp_connection.cwd.assert_called_once_with(destination.directory)
        mock_ftp_connection.storbinary.assert_called_once_with(
            f"STOR {filename}", mp3.file
        )
        mock_ftp_connection.quit.assert_called_once()
        self.assertEqual(len(mock_ftp_connection.method_calls), call_count)
