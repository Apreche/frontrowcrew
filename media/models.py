import os

from django.db import models
from django.utils.translation import gettext_lazy as _

from . import id3
from . import ftp
from . import xmp


class MP3(models.Model):
    upload_time = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="MP3/")

    def get_xmp_chapters(self):
        return xmp.get_xmp_chapters(self.file)

    def get_info(self):
        return id3.get_info(self.file)

    def get_id3(self):
        return id3.get_id3(self.file)

    def set_id3(self, *args, **kwargs):
        return id3.set_id3(self.file, *args, **kwargs)

    def __str__(self):
        return os.path.basename(
            self.file.name
        )

    class Meta:
        verbose_name = _("MP3")
        verbose_name_plural = _("MP3s")
        get_latest_by = ["-upload_time"]


class FTPDestination(models.Model):
    name = models.TextField()
    host = models.TextField()
    username = models.TextField(blank=True, default="")
    password = models.TextField(blank=True, default="")
    directory = models.TextField(blank=True, default="")
    custom_timeout = models.SmallIntegerField(blank=True, null=True, default=None)

    url_prefix = models.TextField(
        blank=True, default="",
        help_text=_("The URL at which the file will be available after uploading."),
        verbose_name=_("URL Prefix"),
    )

    def __str__(self):
        return self.name

    def upload(self, file, filename):
        return ftp.upload_file_to_destination(self, file, filename)

    class Meta:
        verbose_name = _("FTP Destination")
        verbose_name_plural = _("FTP Destinations")
