import os
import tempfile

from django import test

from betafrontrowcrew.tests import utils
from shows import factories, models


@test.override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "betafrc_test_media"),
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class RelatedLinkTests(utils.FRCTestCase):

    def test_related_link_publishable_manager(self):
        published_link = factories.RelatedLinkFactory(
            published=True
        )
        self.assertIn(
            published_link,
            models.RelatedLink.published.all()
        )
        self.assertIn(
            published_link,
            models.RelatedLink.objects.all()
        )

        unpublished_link = factories.RelatedLinkFactory(
            unpublished=True,
        )
        self.assertNotIn(
            unpublished_link,
            models.RelatedLink.published.all()
        )
        self.assertIn(
            unpublished_link,
            models.RelatedLink.objects.all()
        )
