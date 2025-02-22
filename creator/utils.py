from creator import tasks


def create_podcast_episode(episode):
    tasks.sort_chapters.configure(lock=str(episode.id)).defer(episode_id=episode.id)
    tasks.apply_id3_tags.configure(lock=str(episode.id)).defer(episode_id=episode.id)
    tasks.upload_file.configure(lock=str(episode.id)).defer(episode_id=episode.id)
    tasks.publish_podcast_episode.configure(lock=str(episode.id)).defer(
        episode_id=episode.id
    )
