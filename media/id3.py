import os
import PIL
import tempfile

from django.utils import timezone

from mutagen import (
    mp3 as mutagen_mp3,
    id3 as mutagen_id3
)


def get_info(mp3_file):
    """ Get current ID3 tags from file """
    mp3_file.seek(0)
    retval = mutagen_mp3.MP3(mp3_file).info
    mp3_file.seek(0)
    return retval


def get_id3(mp3_file):
    """ Get current ID3 tags from file """
    mp3_file.seek(0)
    retval = mutagen_mp3.MP3(mp3_file).tags
    mp3_file.seek(0)
    return retval


def set_id3(
    mp3_file,
    *args,
    title=None,
    performer=None,
    album=None,
    content_type="Podcast",
    description=None,
    recording_time=None,
    release_time=None,
    tag_time=None,
    feed_url=None,
    artist_web_page=None,
    copyright_info=None,
    copyright_url=None,
    detail_url=None,
    album_image=None,
    album_image_description="",
    chapters=[],
    **kwargs,
):
    """ Overwrite ID3 tags on MP3 file """
    if tag_time is None:
        tag_time = timezone.now().strftime("%Y-%m-%dT%H:%M:%S")

    frames = []

    # Text Frames
    text_frames = {
        "TIT2": ("text", title),
        "TPE1": ("text", performer),
        "TALB": ("text", album),
        "TCON": ("text", content_type),
        "TCOP": ("text", copyright_info),
        "TDES": ("text", description),
        "TDRC": ("text", recording_time),
        "TDRL": ("text", release_time),
        "TDTG": ("text", tag_time),
        "WFED": ("url", feed_url),
        "WOAR": ("url", artist_web_page),
        "WCOP": ("url", copyright_url),
        "WOAF": ("url", detail_url),
    }
    for frame_name, frame_data in text_frames.items():
        frame = getattr(mutagen_id3, frame_name)
        frame_param, value = frame_data
        if value:
            params = {frame_param: value}
            frames.append(
                frame(**params)
            )

    # APIC frame
    permitted_image_formats = {
        "JPEG": "image/jpeg",
        "PNG": "image/png",
    }
    if album_image:
        image = PIL.Image.open(album_image)
        mime_type = permitted_image_formats.get(image.format, None)
        if mime_type is not None:
            image.seek(0)
            APIC_frame = mutagen_id3.APIC(
                mime=mime_type,
                data=image.fp.read(),
            )
            if album_image_description:
                APIC_frame.desc = album_image_description
            frames.append(APIC_frame)

    # Chapter frames
    if chapters:
        chapter_ids = []
        for number, chapter in enumerate(chapters):
            chapter_title_frame = mutagen_id3.TIT2(
                text=chapter.get("name", f"Chapter {number:02}"),
            )
            chapter_sub_frames = [chapter_title_frame]

            chapter_description = chapter.get("description", None)
            if chapter_description:
                chapter_description_frame = mutagen_id3.TIT3(
                    text=chapter_description
                )
                chapter_sub_frames.append(chapter_description_frame)

            chapter_url = chapter.get("url", None)
            if chapter_url:
                chapter_url_frame = mutagen_id3.WXXX()
                chapter_url_frame.url = chapter_url
                url_description = chapter.get("url_description", None)
                if url_description:
                    chapter_url_frame.desc = url_description
                chapter_sub_frames.append(chapter_url_frame)

            chapter_image = chapter.get("image", None)
            if chapter_image:
                chapter_image = PIL.Image.open(chapter_image)
                mime_type = permitted_image_formats.get(chapter_image.format, None)
                if mime_type is not None:
                    chapter_image.seek(0)
                    APIC_frame = mutagen_id3.APIC(
                        mime=mime_type,
                        data=chapter_image.fp.read(),
                    )
                    image_description = chapter.get("image_description", None)
                    if image_description:
                        APIC_frame.desc = image_description
                    chapter_sub_frames.append(APIC_frame)

            chapter_id = f"ch{number:02}"
            chapter_ids.append(chapter_id)
            chapter_params = {
                "element_id": chapter_id,
                "sub_frames": chapter_sub_frames,
            }
            start_time = chapter.get("start_time", None)
            if start_time is not None:
                chapter_params["start_time"] = start_time
                end_time = chapter.get("end_time", None)
                if end_time:
                    chapter_params["end_time"] = end_time
            frames.append(
                mutagen_id3.CHAP(**chapter_params)
            )
        # Table of Contents
        toc_title_frame = mutagen_id3.TIT2(
            text="Table of Contents",
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
        temp3.write(mp3_file.read())
        tags = mutagen_mp3.MP3(temp3).tags
        for frame in frames:
            tags.add(frame)
        tags.save(temp3, v1=mutagen_id3.ID3v1SaveOptions.CREATE)
        mp3_basename = os.path.basename(mp3_file.name)
        mp3_file.save(mp3_basename, temp3)
