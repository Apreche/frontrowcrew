import celery


def create_podcast_episode(self):
    # 1. Update ID3 tag on file
    update_id3_task = celery.signature(
        "media.tasks.apply_id3_tags",
    )
    # 2. Upload file
    # 3. Create podcast enclosure
    # 4. Create podcast episode
    # 5. Create podcast chapters
    # 6. Create show content
    # 7. Create related links
    # 8. Post to other platforms

    # 3, 2, 1, GO!
    celery.chain(update_id3_task)
