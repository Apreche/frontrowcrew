import tqdm
from django.core.management.base import BaseCommand
from shows import models as show_models


class Command(BaseCommand):
    help = "Rerender all the content html"

    def handle(self, *args, **options) -> None:
        for content in tqdm.tqdm(
            show_models.Content.objects.all()
        ):
            # Because of signals, this should be enough to re-render
            content.save()
