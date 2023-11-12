import http
import logging

import requests
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _

from shows import models as show_models

from .syndication import Syndicator

logger = logging.getLogger(__name__)


class Discord(Syndicator):
    name = models.TextField(unique=True)
    webhook_url = models.URLField()
    server_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        default=None,
        help_text=_("Option. Set this to enable automatic related link generation."),
    )
    thread_channel = models.BooleanField(
        default=False,
        help_text=_("Set to true if the webhook is attached to a forum channel."),
    )

    def __str__(self) -> str:
        return f"Discord syndicator - {self.name}"

    def format_content(self, content):
        # For discord, just post a bunch of URLs, and let embeds take care of the rest
        content_list = []
        domain = Site.objects.get_current().domain
        path = content.get_absolute_url()
        content_list.append(f"https://{domain}{path}")
        content_list += [e.external_link for e in content.embedded_media.all()]
        content_list += [rl.url for rl in content.related_links.all()]
        return "\n".join(content_list)

    def post(self, content):
        params = {"wait": True}
        payload = {
            "content": self.format_content(content),
        }
        if self.thread_channel:
            payload["thread_name"] = content.title
        response = requests.post(self.webhook_url, params=params, data=payload)
        if response.status_code != http.HTTPStatus.OK:
            logger.error(
                f"{content} failed to syndicate to Discord - {response.status_code} - response.content"
            )
            return False
        logger.info(f"{content} syndicated to Discord - {self.name}")
        return response.json()

    def create_related_link(self, content, post_result):
        if not self.server_id:
            return
        channel_id = post_result.get("channel_id")
        message_id = post_result.get("id")
        url = f"https://discord.com/channels/{self.server_id}/{channel_id}/{message_id}"
        show_models.RelatedLink.objects.create(
            content=content,
            type_id=show_models.RelatedLinkType.DISCORD_CHAT,
            title=content.title,
            description=f"Discord chat for {content.title}",
            url=url,
        )
