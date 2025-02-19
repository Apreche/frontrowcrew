from procrastinate.contrib.django import app as procrastinate_app

from creator import models
from frontrowcrew.utils import tasks as task_utils


@procrastinate_app.task
@task_utils.plug_psycopg_leak
def upload_file(episode_id):
    episode = models.Episode.objects.get(id=episode_id)
    episode.destination.upload(
        episode.mp3.file,
        f"{episode.catalog_number}.mp3",
    )
