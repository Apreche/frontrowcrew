import celery
from creator import tasks


def create_podcast_episode(episode):

    task_chain = celery.chain(
        tasks.sort_chapters.si(episode.id),
        tasks.apply_id3_tags.si(episode.id),
        tasks.upload_file.si(episode.id),
        tasks.publish_podcast_episode.si(episode.id),
        # TODO: Social Media Posting
    )
    result = task_chain()
    return result.get()
