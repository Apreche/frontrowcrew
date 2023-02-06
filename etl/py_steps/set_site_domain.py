from django.conf import settings
from django.contrib.sites import models as site_models


def run() -> None:
    site = site_models.Site.objects.first()
