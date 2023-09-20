import requests
from http import HTTPStatus
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from podcasts import models as podcast_models
from media import models as media_models


class Command(BaseCommand):
    help = "Make sure all the podcast enclosure MP3s are backed up"

    def handle(self, *args, **options) -> None:

        enclosures = podcast_models.PodcastEnclosure.objects.filter(
            type=podcast_models.PodcastEnclosure.EnclosureType.MP3,
        )

        upload_to = media_models.MP3.file.field.upload_to

        for enclosure in enclosures:
            filename = requests.utils.urlparse(
                enclosure.url
            ).path.split("/").pop()
            filepath = f"{upload_to}{filename}"

            try:
                mp3 = media_models.MP3.objects.get(file=filepath)
                continue
            except media_models.MP3.DoesNotExist:
                pass

            response = requests.get(enclosure.url)
            if response.status_code != HTTPStatus.OK:
                print(f"[{response.status_code}] {enclosure.url}")
                continue
            file = ContentFile(response.content, name=filename)
            mp3 = media_models.MP3(
                file=file
            )
            mp3.save()
