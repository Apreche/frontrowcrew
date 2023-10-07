"""global utils for frontrowcrew"""
from django.contrib.sites import models as sites_models
from django.conf import settings


def default_base_url():
    """ get the current default base url """
    site = sites_models.Site.objects.get_current()
    domain = site.domain
    protocol = getattr(settings, "DEFAULT_PROTOCOL")
    return f"{protocol}://{domain}/"
