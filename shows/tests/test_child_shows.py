import os
import tempfile

from django import test

from frontrowcrew.tests import utils

from .. import factories


@test.override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=os.path.join(tempfile.gettempdir(), "frc_test_media"),
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "ChildShowTest",
        }
    },
)
class ChildShowTests(utils.FRCTestCase):
    def test_child_show_includes(self):
        """
        Test if content of a child-show is included on the parent show
        """
        content = factories.ContentFactory(
            show__is_published=True,
            is_published=True,
        )
        child_show = content.show
        parent_show = factories.ShowFactory(
            is_published=True,
        )
        child_show.parent_show = parent_show
        child_show.save()
        self.assertIn(
            content,
            parent_show.published_content,
        )

    def test_child_show_mixed_includes(self):
        """
        Test if content directly on parent show is properly mixed with content
        from child shows.
        """
        content = factories.ContentFactory(
            show__is_published=True,
            is_published=True,
        )
        child_show = content.show
        parent_show = factories.ShowFactory(
            is_published=True,
        )
        parent_content = factories.ContentFactory(
            show=parent_show,
            is_published=True,
        )
        child_show.parent_show = parent_show
        child_show.save()
        self.assertIn(
            content,
            parent_show.published_content,
        )
        self.assertIn(
            parent_content,
            parent_show.published_content,
        )

    def test_parent_show_unpublished_includes(self):
        """
        Published content on an unpublished child show should not appear even if
        the parent show is published.
        """
        content = factories.ContentFactory(
            show__is_published=False,
            is_published=True,
        )
        child_show = content.show
        parent_show = factories.ShowFactory(
            is_published=True,
        )
        parent_content = factories.ContentFactory(
            show=parent_show,
            is_published=True,
        )
        child_show.parent_show = parent_show
        child_show.save()
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
        Even if a parent show is unpublished, a published child show should still
        be working independently of it.
        """
        content = factories.ContentFactory(
            show__is_published=True,
            is_published=True,
        )
        child_show = content.show
        parent_show = factories.ShowFactory(
            is_published=False,
        )
        parent_content = factories.ContentFactory(
            show=parent_show,
            is_published=True,
        )
        child_show.parent_show = parent_show
        child_show.save()
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
            child_show.published_content,
        )

    def test_child_show_depth_is_one(self):
        """
        Child shows are not evaluated recursively.
        Only content from immediate children is included.
        """
        content = factories.ContentFactory(
            show__is_published=True,
            is_published=True,
        )
        child_child_show = content.show
        child_show = factories.ShowFactory(is_published=True)
        child_child_show.parent_show = child_show
        child_child_show.save()
        parent_show = factories.ShowFactory(is_published=True)
        child_show.parent_show = parent_show
        child_show.save()
        self.assertIn(
            content,
            child_child_show.published_content,
        )
        self.assertIn(
            content,
            child_show.published_content,
        )
        self.assertNotIn(
            content,
            parent_show.published_content,
        )
