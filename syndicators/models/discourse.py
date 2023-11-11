import http
import logging

import requests
from django.db import models

from shows import models as show_models

from .syndication import Syndicator

logger = logging.getLogger(__name__)


class Discourse(Syndicator):
    url = models.URLField()
    api_key = models.TextField()
    username = models.TextField()
    category_id = models.IntegerField()

    def __str__(self) -> str:
        return f"Discourse syndicator for {self.username} @ {self.url}"

    def format_content(self, content):
        formatted_content = super().format_content(content)
        embedded_media = content.embedded_media.all()
        if not embedded_media:
            return formatted_content
        for embed in embedded_media:
            formatted_content += f"\n{embed.external_link}\n"
        return formatted_content

    def post(self, content):
        post_url = f"{self.url}/posts.json"
        headers = {"Api-Key": self.api_key, "Api-Username": self.username}
        payload = {
            "title": f"{content.show.title} - {content.title}",
            "raw": self.format_content(content),
            "category": self.category_id,
        }
        response = requests.post(
            post_url,
            headers=headers,
            data=payload,
        )
        if response.status_code != http.HTTPStatus.OK:
            logger.error(
                f"{content} failed to publish to Discourse - {response.status_code} - {response.content}"
            )
            return False
        return response.json()

    def create_related_link(self, content, post_result):
        topic_slug = post_result.get("topic_slug", "")
        topic_id = post_result.get("topic_id", "")
        post_url = f"{self.url}/t/{topic_slug}/{topic_id}"
        show_models.RelatedLink.objects.create(
            content=content,
            type_id=show_models.RelatedLinkType.FORUM_THREAD,
            title=content.title,
            description=f"Forum discussion for {content.title}",
            url=post_url,
        )
        logger.info(f"{content} published to Discourse")
