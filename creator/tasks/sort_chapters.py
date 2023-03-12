import celery

from mutagen import mp3 as mutagen_mp3

from creator import models


@celery.shared_task
def sort_chapters(episode_id):
    """
    Recalculate and fill in the start and end times on all chapters
    """
    episode = models.Episode.objects.get(
        id=episode_id,
        processed=False,
    )
    mp3_file = mutagen_mp3.MP3(episode.mp3.file)
    mp3_end_time = int(mp3_file.info.length * 1000)
    chapters = models.Chapter.objects.filter(
        episode=episode
    ).order_by("-start_time")

    previous_start_time = None
    for chapter in chapters:
        if not chapter.end_time:
            if previous_start_time is None:
                chapter.end_time = mp3_end_time
            else:
                chapter.end_time = previous_start_time - 1
            chapter.save()
        previous_start_time = chapter.start_time
