from mutagen import mp3 as mutagen_mp3
from procrastinate.contrib.django import app as procrastinate_app

from creator import models
from frontrowcrew.utils import tasks as task_utils


@procrastinate_app.task
@task_utils.plug_psycopg_leak
def sort_chapters(episode_id):
    """
    Recalculate and fill in the start and end times on all chapters
    """
    episode = models.Episode.objects.get(
        id=episode_id,
        processed=False,
    )
    original_file = episode.mp3.file
    mp3_file = mutagen_mp3.MP3(original_file)
    mp3_end_time = int(mp3_file.info.length * 1000)
    chapters = models.Chapter.objects.filter(episode=episode).order_by("-start_time")

    previous_start_time = None
    for chapter in chapters:
        if not chapter.end_time:
            if previous_start_time is None:
                chapter.end_time = mp3_end_time
            else:
                chapter.end_time = previous_start_time - 1
            chapter.save()
        previous_start_time = chapter.start_time
    original_file.close()
