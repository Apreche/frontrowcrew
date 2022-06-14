import ftplib
import libxmp
import PIL
import tempfile

from libxmp import utils as xmp_utils
from mutagen import (
    mp3 as mutagen_mp3,
    id3 as mutagen_id3
)
from django.db import models
from django.utils import timezone


class MP3(models.Model):
    file = models.FileField(upload_to="MP3/")

    def __str__(self):
        return self.file.name

    def get_xmp_chapters(self):
        """ Extract the XMP chapters that Adobe Audition puts in the ID3 PRIV tag """

        XMP_FRAMERATE_KEY = "xmpDM:Tracks[1]/xmpDM:frameRate"
        XMP_CHAPTER_NAME_KEY = "xmpDM:Tracks[1]/xmpDM:markers[{number}]/xmpDM:name"
        XMP_CHAPTER_START_TIME_KEY = "xmpDM:Tracks[1]/xmpDM:markers[{number}]/xmpDM:startTime"

        chapters = []
        self.file.seek(0)
        id3_tags = mutagen_mp3.MP3(self.file).tags
        self.file.seek(0)
        raw_rdf, *_ = id3_tags.getall("PRIV")
        with tempfile.NamedTemporaryFile() as temp_xmp_file:
            temp_xmp_file.write(raw_rdf.data)
            temp_xmp_file.seek(0)
            try:
                xmp = xmp_utils.file_to_dict(temp_xmp_file.name)
            except Exception:
                return chapters
        ns_dm = xmp.get(libxmp.consts.XMP_NS_DM, None)
        if ns_dm is None:
            return chapters
        dm = {key: value for key, value, *_ in ns_dm}
        frame_rate_string = dm.get(XMP_FRAMERATE_KEY, None)
        if frame_rate_string is None:
            return chapters
        frame_rate = int("".join(frame_rate_string[1:]))
        marker_number = 1
        while True:
            name_key = XMP_CHAPTER_NAME_KEY.format(number=marker_number)
            chapter_name = dm.get(name_key, None)
            if chapter_name is None:
                break

            time_key = XMP_CHAPTER_START_TIME_KEY.format(number=marker_number)
            time_string = dm.get(time_key, None)
            if time_string is None:
                break

            frame_number = int(time_string)
            chapter_start_time = frame_number / frame_rate
            chapters.append(
                {
                    "name": chapter_name,
                    "time": chapter_start_time,
                }
            )
            marker_number += 1
        sorted_chapters = sorted(
            chapters,
            key=lambda d: d.get("time", None)
        )
        return sorted_chapters

    def get_id3(self):
        """ Get current ID3 tags from file """
        self.file.seek(0)
        retval = mutagen_mp3.MP3(self.file).tags
        self.file.seek(0)
        return retval

    def set_id3(
        self,
        title=None,
        performer=None,
        album=None,
        content_type="Podcast",
        description=None,
        recording_time=None,
        release_time=None,
        tag_time=None,
        recording_year=None,
        feed_url=None,
        artist_web_page=None,
        copyright_info=None,
        detail_url=None,
        album_image=None,
        album_image_description=None,
        chapters=[],
    ):
        """ Overwrite ID3 tags on MP3 file """
        if tag_time is None:
            tag_time = timezone.now().stftime("%Y-%m-%dT%H:%M:%S")

        frames = []

        # Text Frames
        text_frames = {
            "TIT2": title,
            "TPE1": performer,
            "TALB": album,
            "TCON": content_type,
            "TDES": description,
            "TDRC": recording_time,
            "TDRL": release_time,
            "TDTG": tag_time,
            "TYER": recording_year,
            "WFED": feed_url,
            "WOAR": artist_web_page,
            "WCOP": copyright_info,
            "WOAF": detail_url,
        }
        for frame_name, value in text_frames.items():
            frame = getattr(mutagen_id3, frame_name)
            if value is not None:
                frames.append(
                    frame(
                        encoding=mutagen_id3.ENCODING.UTF8,
                        text=value,
                    )
                )

        # APIC frame
        permitted_image_formats = {
            "JPEG": "image/jpeg",
            "PNG": "image/png",
        }
        if album_image:
            try:
                image = PIL.Image.open(album_image)
            except Exception:
                pass
            if image.format in permitted_image_formats:
                album_image.seek(0)
                APIC_kwargs = {
                    "encoding": mutagen_id3.ENCODING.UTF8,
                    "mime": permitted_image_formats[image.format],
                    "data": album_image.read()
                }
                if album_image_description:
                    APIC_kwargs["desc"] = album_image_description
                frames.append(mutagen_id3.APIC(**APIC_kwargs))

        # Chapter frames
        if chapters:
            chapter_ids = []
            for number, chapter in enumerate(chapters):
                chapter_title_frame = mutagen_id3.TIT2(
                    encoding=mutagen_id3.ENCODING.UTF8,
                    text=chapter.get("name", f"Chapter {number:02}"),
                )
                chapter_id = f"ch{number:02}"
                chapter_ids.append(chapter_id)
                frames.append(
                    mutagen_id3.CHAP(
                        element_id=chapter_id,
                        start_time=chapter.get("start_time", 0),
                        end_time=chapter.get("end_time", 0),
                        sub_frames=[chapter_title_frame]
                    )
                )
            # Table of Contents
            toc_title_frame = mutagen_id3.TIT2(
                encoding=mutagen_id3.ENCODING.UTF8,
                text=chapter.get("name", "Table of Contents"),
            )
            frames.append(
                mutagen_id3.CTOC(
                    element_id="toc",
                    flags=mutagen_id3.CTOCFlags.TOP_LEVEL | mutagen_id3.CTOCFlags.ORDERED,
                    child_element_ids=chapter_ids,
                    sub_frames=[toc_title_frame],
                )
            )

        # Write frames to file
        with tempfile.NamedTemporaryFile() as temp3:
            temp3.write(self.file.read())
            tags = mutagen_mp3.MP3(temp3).tags
            for frame in frames:
                tags.add(frame)
            tags.save(temp3, v1=mutagen_id3.ID3v1SaveOptions.CREATE)
            self.file.save(self.file.name, temp3)

    class Meta:
        verbose_name = "MP3"
        verbose_name_plural = "MP3s"


class FTPDestination(models.Model):
    name = models.TextField()
    host = models.TextField()
    username = models.TextField(blank=True, default="")
    password = models.TextField(blank=True, default="")
    directory = models.TextField(blank=True, default="")
    custom_timeout = models.SmallIntegerField(blank=True, default=None)

    url_prefix = models.TextField(
        blank=True, default="",
        help_text="The URL at which the file will be available after uploading."
    )

    def __str__(self):
        return self.name

    def upload(self, file, filename):
        """ Upload a file to this FTP destination """
        ftp_kwargs = {
            "host": self.host,
        }
        for field, kwarg in [
            ("username", "user"),
            ("password", "passwd"),
            ("custom_timeout", "timeout"),
        ]:
            value = getattr(self, field, None)
            if value:
                ftp_kwargs[kwarg] = value
        ftp_connection = ftplib.FTP(**ftp_kwargs)
        ftp_connection.storbinary(f"STOR {filename}", file)
        ftp_connection.quit()
        return f"{self.url_prefix}{filename}"
