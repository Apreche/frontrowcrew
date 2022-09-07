import celery
from django import utils as django_utils
from django import urls

from betafrontrowcrew.utils import sites
from media import models as media_models
from podcasts import models as podcast_models
from shows import models as show_models


@celery.shared_task(bind=True)
def apply_id3_tags(
    self,
    mp3_id,
    show_id,
    podcast_id,
    title,
    description,
    pub_time,
    catalog_number,
    image_description,
):
    try:
        mp3 = media_models.MP3.objects.get(id=mp3_id)
        show = show_models.Show.objects.get(id=show_id)
        podcast = podcast_models.Podcast.objects.get(id=podcast_id)
    except (
        media_models.MP3.DoesNotExist,
        show_models.Show.DoesNotExist,
        podcast_models.Podcast.DoesNotExist,
    ) as exc:
        raise self.retry(exc=exc)

    # main_data = podcast_data.get("main_data")

    content_slug = django_utils.text.slugify(title)
    default_feed_url = urls.reverse(
        "show-podcast-rss",
        args=[show.slug]
    )

    id3_data = {
        "title": title,
        "performer": podcast.itunes_author,
        "album": podcast.title,
        "content_type": "Podcast",
        "description": description,
        # "recording_time": None,  #  Leave whatever was set by recording app
        "release_time": pub_time.astimezone(
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
                catalog_number,
                content_slug,
            ]
        ),
        "album_image_description": image_description,
    }
    album_image = None
    album_image_data = main_data.get("image", None)
    if album_image_data:
        album_image = album_image_data.open("rb")
    elif podcast.image:
        album_image = podcast.image.open("rb")

    id3_data["album_image"] = album_image
    mp3.set_id3(**id3_data)

    if album_image:
        album_image.close()
