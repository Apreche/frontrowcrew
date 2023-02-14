import hashlib
from etl import utils as etl_utils
from embeds import models as embed_models
from shows import models as show_models


def run() -> None:
    """
    Get all the video thumbnails from YouTube
    """
    storage = show_models.Content._meta.get_field("image").storage
    for embed in embed_models.Media.objects.all():
        youtube_id = embed.media_id
        download_params = {
            "old_path": f"{youtube_id}/maxresdefault.jpg",
            "new_filename": f"{youtube_id}.jpg",
            "old_base_url": "https://img.youtube.com/vi/",
            "new_base_path": show_models.Content._meta.get_field("image").upload_to,
        }
        new_path = etl_utils.download_to_default_storage(
            **download_params
        )
        file = storage.open(new_path)
        md5_hash = hashlib.md5(file.read()).hexdigest()
        # Detect the YouTube ... images
        bad_hash = "e2ddfee11ae7edcae257da47f3a78a70"
        if md5_hash == bad_hash:
            storage.delete(new_path)
            download_params["old_path"] = f"{youtube_id}/hqdefault.jpg"
            new_path = etl_utils.download_to_default_storage(
                **download_params
            )

        content = embed.content_set.all().first()
        content.image.name = new_path
        content.save()
