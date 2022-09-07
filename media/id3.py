import PIL
import tempfile

from django.utils import timezone

from mutagen import (
    mp3 as mutagen_mp3,
    id3 as mutagen_id3
)


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
    recording_year=None,
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
        "TIT2": title,
        "TPE1": performer,
        "TALB": album,
        "TCON": content_type,
        "TCOP": copyright_info,
        "TDES": description,
        "TDRC": recording_time,
        "TDRL": release_time,
        "TDTG": tag_time,
        "TYER": recording_year,
        "WFED": feed_url,
        "WOAR": artist_web_page,
        "WCOP": copyright_url,
        "WOAF": detail_url,
    }
    for frame_name, value in text_frames.items():
        frame = getattr(mutagen_id3, frame_name)
        if value is not None:
            frames.append(
                frame(
                    text=value,
                )
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
            if chapter_description is not None:
                chapter_description_frame = mutagen_id3.TIT3(
                    text=chapter_description
                )
                chapter_sub_frames.append(chapter_description_frame)

            chapter_url = chapter.get("url", "")
            if chapter_url:
                chapter_url_frame = mutagen_id3.WXXX()
                chapter_url_frame.url = chapter_url
                chapter_url_frame.desc = chapter.get("url_description", "")
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
                    APIC_frame.desc = chapter.get("image_description", "")
                    chapter_sub_frames.append(APIC_frame)

            chapter_id = f"ch{number:02}"
            chapter_ids.append(chapter_id)
            frames.append(
                mutagen_id3.CHAP(
                    element_id=chapter_id,
                    start_time=chapter.get("start_time", 0),
                    end_time=chapter.get("end_time", 0),
                    sub_frames=chapter_sub_frames,
                )
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
        mp3_file.save(mp3_file.name, temp3)
#
