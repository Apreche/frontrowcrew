from betafrontrowcrew.tests import utils
from shows import factories, models


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
