import celery

from creator import models


@celery.shared_task
def upload_file(episode_id):
    episode = models.Episode.objects.get(id=episode_id)
    episode.destination.upload(
        episode.mp3.file,
        f"{episode.catalog_number}.mp3",
    )
