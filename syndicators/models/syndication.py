import logging

from django.db import models
from model_utils import managers as model_util_managers

logger = logging.getLogger(__name__)


class Syndicator(models.Model):
    objects = model_util_managers.InheritanceManager()

    shows = models.ManyToManyField("shows.Show", blank=True)

    def format_content(self, content):
        return content.rendered_html_with_related_links

    def post(self, content):
        logger.warning(f"{content} attempted to post with unimplemented method")

    def create_related_link(self, content, post_result):
        logger.warning(
            f"{content} attempted to create related link with unimplemented method"
        )

    def syndicate(self, content):
        post_result = self.post(content)
        self.create_related_link(content, post_result)
