import tempfile
#
import libxmp
from libxmp import utils as xmp_utils

from mutagen import mp3 as mutagen_mp3

XMP_FRAMERATE_KEY = "xmpDM:Tracks[1]/xmpDM:frameRate"
XMP_CHAPTER_NAME_KEY = "xmpDM:Tracks[1]/xmpDM:markers[{number}]/xmpDM:name"
XMP_CHAPTER_START_TIME_KEY = "xmpDM:Tracks[1]/xmpDM:markers[{number}]/xmpDM:startTime"


def get_xmp_chapters(mp3_file):
    """ Extract the XMP chapters that Adobe Audition puts in the ID3 PRIV tag """

    chapters = []
    mp3_file.seek(0)
    id3_tags = mutagen_mp3.MP3(mp3_file).tags
    mp3_file.seek(0)
    priv_tags = id3_tags.getall("PRIV")
    if not priv_tags:
        return chapters
    raw_rdf, *_ = priv_tags
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
        chapter_title = dm.get(name_key, None)
        if chapter_title is None:
            break

        time_key = XMP_CHAPTER_START_TIME_KEY.format(number=marker_number)
        time_string = dm.get(time_key, None)
        if time_string is None:
            break

        frame_number = int(time_string)
        chapter_start_time = round((frame_number / frame_rate) * 1000)
        chapters.append(
            {
                "title": chapter_title,
                "time": chapter_start_time,
            }
        )
        marker_number += 1
    sorted_chapters = sorted(
        chapters,
        key=lambda d: d.get("time", None)
    )
    return sorted_chapters
