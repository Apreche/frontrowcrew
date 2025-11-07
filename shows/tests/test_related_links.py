import os
import tempfile

from django import test
from django.conf import global_settings

from frontrowcrew.tests import utils
from shows import factories, models


@test.override_settings(
    STORAGES=global_settings.STORAGES,
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "frc_test_media"),
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "RelatedLinkTest",
        }
    },
)
class RelatedLinkTests(utils.FRCTestCase):
    def test_related_link_publishable_manager(self):
        published_link = factories.RelatedLinkFactory(published=True)
        self.assertIn(published_link, models.RelatedLink.published.all())
        self.assertIn(published_link, models.RelatedLink.objects.all())

        unpublished_link = factories.RelatedLinkFactory(
            unpublished=True,
        )
        self.assertNotIn(unpublished_link, models.RelatedLink.published.all())
        self.assertIn(unpublished_link, models.RelatedLink.objects.all())
