from betafrontrowcrew.tests import utils
from .. import factories


class SubShowTests(utils.FRCTestCase):

    def test_sub_show_includes(self):
        """
        Test if content of a sub-show is included on the parent show
        """
        content = factories.ContentFactory(
            show__is_published=True,
            is_published=True,
        )
        sub_show = content.show
        parent_show = factories.ShowFactory(
            is_published=True,
        )
        parent_show.sub_shows.add(sub_show)
        self.assertIn(
            content,
            parent_show.published_content,
        )

    def test_sub_show_mixed_includes(self):
        """
        Test if content directly on parent show is properly mixed with content
        from sub shows.
        """
        content = factories.ContentFactory(
            show__is_published=True,
            is_published=True,
        )
        sub_show = content.show
        parent_show = factories.ShowFactory(
            is_published=True,
        )
        parent_content = factories.ContentFactory(
            show=parent_show,
            is_published=True,
        )
        parent_show.sub_shows.add(sub_show)
        self.assertIn(
            content,
            parent_show.published_content,
        )
        self.assertIn(
            parent_content,
            parent_show.published_content,
        )

    def test_sub_show_unpublished_includes(self):
        """
        Published content on an unpublished sub-show should not appear even if
        the parent show is published.
        """
        content = factories.ContentFactory(
            show__is_published=False,
            is_published=True,
        )
        sub_show = content.show
        parent_show = factories.ShowFactory(
            is_published=True,
        )
        parent_content = factories.ContentFactory(
            show=parent_show,
            is_published=True,
        )
        parent_show.sub_shows.add(sub_show)
        self.assertNotIn(
            content,
            parent_show.published_content,
        )
        self.assertIn(
            parent_content,
            parent_show.published_content,
        )

    def test_parent_show_unpublished(self):
        """
        Even if a parent show is unpublished, a published sub-show should still
        be working independently of it.
        """
        content = factories.ContentFactory(
            show__is_published=True,
            is_published=True,
        )
        sub_show = content.show
        parent_show = factories.ShowFactory(
            is_published=False,
        )
        parent_content = factories.ContentFactory(
            show=parent_show,
            is_published=True,
        )
        parent_show.sub_shows.add(sub_show)
        self.assertNotIn(
            content,
            parent_show.published_content,
        )
        self.assertNotIn(
            parent_content,
            parent_show.published_content,
        )
        self.assertIn(
            content,
            sub_show.published_content,
        )

    def test_sub_show_depth_is_one(self):
        """
        Sub-shows are not evaluated recursively.
        Only content from immediate children is included.
        """
        content = factories.ContentFactory(
            show__is_published=True,
            is_published=True,
        )
        sub_sub_show = content.show
        sub_show = factories.ShowFactory(
            is_published=True
        )
        sub_show.sub_shows.add(sub_sub_show)
        parent_show = factories.ShowFactory(
            is_published=True
        )
        parent_show.sub_shows.add(sub_show)
        self.assertIn(
            content,
            sub_sub_show.published_content,
        )
        self.assertIn(
            content,
            sub_show.published_content,
        )
        self.assertNotIn(
            content,
            parent_show.published_content,
        )
