import datetime
import celery
from django.db import transaction
from django.utils import text as text_utils

from creator import models
from podcasts import models as podcast_models
from shows import models as show_models


class ConflictingContentException(Exception):
    pass


@celery.shared_task
def publish_podcast_episode(episode_id):
    with transaction.atomic():
        creator_episode = models.Episode.objects.get(id=episode_id)

        conflicting_content = show_models.Content.objects.filter(
            show=creator_episode.show,
            catalog_number=creator_episode.catalog_number,
        )
        if conflicting_content:
            raise ConflictingContentException(
                f"Content for show {creator_episode.show} "
                f"with catalog number {creator_episode.catalog_number} "
                "already exists."
            )

        url_prefix = creator_episode.destination.url_prefix
        filename = f"{creator_episode.catalog_number}.mp3"
        url = f"{url_prefix}{filename}"
        # 4. Create podcast enclosure
        enclosure = podcast_models.PodcastEnclosure.objects.create(
            url=url,
            length=creator_episode.mp3.file.size,
            type=podcast_models.PodcastEnclosure.EnclosureType.MP3,
        )
        # 5. Create podcast episode
        mp3_info = creator_episode.mp3.get_info()
        duration = datetime.timedelta(seconds=mp3_info.length)
        episode = podcast_models.PodcastEpisode.objects.create(
            podcast=creator_episode.show.podcast,
            title=creator_episode.title,
            enclosure=enclosure,
            pub_date=creator_episode.pub_time,
            description=creator_episode.description,
            duration=duration,
            author_name=creator_episode.author_name,
            author_email=creator_episode.author_email,
            image=creator_episode.image,
            image_description=creator_episode.image_description,
            itunes_image=creator_episode.itunes_image,
            itunes_explicit=creator_episode.itunes_explicit,
            itunes_title=creator_episode.itunes_title,
            itunes_episode_number=creator_episode.itunes_episode_number,
            itunes_season_number=creator_episode.itunes_season_number,
            itunes_episode_type=creator_episode.itunes_episode_type,
            itunes_block=creator_episode.itunes_block,
        )
        # 6. Create podcast chapters
        for chapter in creator_episode.chapters.all():
            podcast_models.PodcastChapter.objects.create(
                episode=episode,
                start_time=chapter.start_time,
                end_time=chapter.end_time,
                title=chapter.title,
                description=chapter.description,
                url=chapter.url,
                url_description=chapter.url_description,
                image=chapter.image,
                image_description=chapter.image_description,
            )
        # 7. Create show content
        content = show_models.Content.objects.create(
            pub_time=creator_episode.pub_time,
            is_published=True,
            title=creator_episode.title,
            show=creator_episode.show,
            image=creator_episode.image,
            image_description=creator_episode.image_description,
            slug=text_utils.slugify(creator_episode.title),
            catalog_number=creator_episode.catalog_number,
            original_content=creator_episode.body,
            podcast_episode=episode,
        )
        for tag in creator_episode.tags.names():
            content.tags.add(tag)
        # 8. Create related links
        for related_link in creator_episode.related_links.all():
            show_models.RelatedLink.objects.create(
                content=content,
                type_id=show_models.RelatedLinkType.THING_OF_THE_DAY,
                title=related_link.title,
                description=related_link.description,
                url=related_link.url,
                author=related_link.author,
            )
        return content.id
