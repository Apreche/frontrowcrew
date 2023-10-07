import celery
from django import utils as django_utils
from django import urls

from frontrowcrew.utils import sites
from creator import models


@celery.shared_task
def apply_id3_tags(
    episode_id
):
    episode = models.Episode.objects.get(
        id=episode_id,
        processed=False,
    )
    mp3 = episode.mp3
    show = episode.show
    podcast = show.podcast

    if not podcast:
        raise Exception("Selected show has no podcast")

    content_slug = django_utils.text.slugify(episode.title)
    default_feed_url = urls.reverse(
        "show-podcast-rss",
        args=[show.slug]
    )

    id3_data = {
        "title": episode.title,
        "performer": podcast.itunes_author,
        "album": podcast.title,
        "content_type": "Podcast",
        "description": episode.description,
        # "recording_time": None,  #  Leave whatever was set by recording app
        "release_time": episode.pub_time.astimezone(
            django_utils.timezone.utc
        ).strftime("%Y-%m-%dT%H:%M"),
        "tag_time": django_utils.timezone.now().strftime("%Y-%m-%dT%H:%M"),
        "feed_url": podcast.custom_public_feed_url or default_feed_url,
        "artist_web_page": sites.default_base_url(),
        "copyright_info": getattr(podcast, "copyright", None),
        "copyright_url": getattr(podcast, "creative_commons_license", None),
        "detail_url": urls.reverse(
            "content-detail",
            args=[
                show.slug,
                episode.catalog_number,
                content_slug,
            ]
        ),
        "album_image_description": episode.image_description,
    }
    album_image = None
    album_image_data = episode.image
    if album_image_data:
        album_image = album_image_data.open("rb")
    elif podcast.image:
        album_image = podcast.image.open("rb")

    id3_data["album_image"] = album_image

    # Chapters
    chapters = []
    for chapter in episode.chapters.all().order_by("start_time"):
        chapter_dict = {
            "name": chapter.title,
            "description": getattr(chapter, "description", None),
            "url": getattr(chapter, "url", None),
            "url_description": getattr(chapter, "url_description", None),
            "start_time": chapter.start_time,
            "end_time": getattr(chapter, "end_time", None),
            "image": getattr(chapter, "image", None),
            "image_description": getattr(chapter, "image_desscription", None),
        }
        chapters.append(chapter_dict)
    if chapters:
        id3_data["chapters"] = chapters

    mp3.set_id3(**id3_data)

    if album_image:
        album_image.close()

    return mp3.id
