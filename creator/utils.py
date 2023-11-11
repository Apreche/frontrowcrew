import celery

from creator import tasks
from syndicators import tasks as syndicator_tasks


def create_podcast_episode(episode):
    celery.chain(
        tasks.sort_chapters.si(episode.id),
        tasks.apply_id3_tags.si(episode.id),
        tasks.upload_file.si(episode.id),
        tasks.publish_podcast_episode.si(episode.id),
        # the publish task returns content_id, which is passed to the syndicator
        syndicator_tasks.full_syndication.s(),
    ).delay()
