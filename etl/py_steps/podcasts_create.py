import typing
import os
from django.core.files import base as django_files_base
from podcasts import models as podcast_models
from shows import models as show_models


def get_itunes_category(
    description: str,
    subcategory_description: str = ""
) -> typing.Union[podcast_models.iTunesCategory, None]:
    """ Lookup an iTunes category matching a string tuple """
    try:
        category = podcast_models.iTunesCategory.objects.get(
            description=description,
            subcategory_description=subcategory_description,
        )
    except podcast_models.iTunesCategory.DoesNotExist:
        return None
    return category


def create_podcast_for_show(
    show_slug: str = "",
    image_description: str = "",
    itunes_owner: typing.Union[podcast_models.iTunesOwner, None] = None,
    custom_public_feed_url: str = "",
    primary_category: typing.Tuple[str, str] = ("Arts", ""),
    secondary_category: typing.Union[typing.Tuple[str, str], None] = None,
) -> None:
    """ Create a podcast for a show using the given data """
    show = show_models.Show.objects.get(slug=show_slug)
    logo_file_name = os.path.basename(show.logo.name)
    logo_file = django_files_base.ContentFile(
        show.logo.read(),
        name=logo_file_name,
    )
    podcast = podcast_models.Podcast(
        title=show.title,
        description=show.description,
        image=logo_file,
        image_description=image_description,
        managing_editor="rym@frontrowcrew.com (Rym DeCoster)",
        web_master="apreche@frontrowcrew.com (Scott Rubin)",
        itunes_image=logo_file,
        itunes_author="Rym and Scott",
        itunes_owner=itunes_owner,
        itunes_primary_category=get_itunes_category(*primary_category),
        copyright="&#xA9; 2005-2022; GeekNights",
        creative_commons_license="https://creativecommons.org/licenses/by/4.0/",
    )
    if secondary_category is not None:
        podcast.itunes_secondary_category = get_itunes_category(*secondary_category)
    if custom_public_feed_url:
        podcast.custom_public_feed_url = custom_public_feed_url
    podcast.save()
    show.podcast = podcast
    show.save()


def run() -> None:
    itunes_owner = podcast_models.iTunesOwner.objects.create(
        name="Scott Rubin",
        email="apreche@frontrowcrew.com",
    )
    podcasts_to_create = [
        {
            "show_slug": "geeknights",
            "image_description": "GeekNights podcast logo",
            "custom_public_feed_url": "https://feeds.feedburner.com/GeekNights",
            "primary_category": ("Leisure", "Hobbies"),
            "secondary_category": ("News", "News Commentary"),
        },
        {
            "show_slug": "monday",
            "image_description": "GeekNights Monday podcast logo",
            "custom_public_feed_url": "https://feeds.feedburner.com/gnscitech",
            "primary_category": ("Technology", ""),
            "secondary_category": ("News", "Tech News"),
        },
        {
            "show_slug": "tuesday",
            "image_description": "GeekNights Tuesday podcast logo",
            "custom_public_feed_url": "https://feeds.feedburner.com/gngaming",
            "primary_category": ("Leisure", "Games"),
            "secondary_category": ("Leisure", "Video Games"),
        },
        {
            "show_slug": "wednesday",
            "image_description": "GeekNights Wednesday podcast logo",
            "custom_public_feed_url": "https://feeds.feedburner.com/gnanime",
            "primary_category": ("Leisure", "Games"),
            "secondary_category": ("Leisure", "Video Games"),
        },
        {
            "show_slug": "thursday",
            "image_description": "GeekNights Thursday podcast logo",
            "custom_public_feed_url": "https://feeds.feedburner.com/gnthursdays",
            "primary_category": ("Leisure", ""),
            "secondary_category": ("Arts", ""),
        },
        {
            "show_slug": "book-club",
            "image_description": "GeekNights Book Club podcast logo",
            "primary_category": ("Arts", "Books"),
        },
        {
            "show_slug": "special",
            "image_description": "GeekNights special podcast logo",
            "primary_category": ("Leisure", ""),
            "secondary_category": ("Arts", ""),
        },
        {
            "show_slug": "experimental",
            "image_description": "GeekNights Experimental podcast logo",
            "custom_public_feed_url": "https://feeds.feedburner.com/gnexperimental",
            "primary_category": ("Leisure", ""),
            "secondary_category": ("Arts", ""),
        },
    ]

    for podcast_data in podcasts_to_create:
        create_podcast_for_show(
            itunes_owner=itunes_owner,
            **podcast_data,
        )
