import logging

from atproto import Client as atpClient
from atproto import models as atp_models
from django.contrib.sites.models import Site
from django.db import models
from django.utils.html import strip_tags

from shows import models as show_models

from .syndication import Syndicator

logger = logging.getLogger(__name__)


class Bluesky(Syndicator):
    username = models.TextField()
    password = models.TextField()

    def __str__(self) -> str:
        return self.username

    def format_content(self, content):
        domain = Site.objects.get_current().domain
        path = content.get_absolute_url()
        return f"https://{domain}{path}"

    def post(self, content):
        client = atpClient()
        client.login(self.username, self.password)

        # Bluesky can't intelligently embed, we need to do it ourselves
        # https://github.com/MarshalX/atproto/blob/main/examples/advanced_usage/send_ogp_link_card.py

        embed_data = {
            "title": content.title,
            "description": strip_tags(content.rendered_html),
            "uri": self.format_content(content),
        }

        image = content.image or content.show.logo or None
        if image:
            image.seek(0)
            image_data = image.read()
            thumb = client.upload_blob(image_data).blob
            embed_data["thumb"] = thumb

        external = atp_models.AppBskyEmbedExternal.External(**embed_data)
        embed_external = atp_models.AppBskyEmbedExternal.Main(external=external)
        response = client.send_post(
            text=content.title,
            embed=embed_external,
        )
        return response.model_dump()

    def create_related_link(self, content, post_result):
        at_uri = post_result.get("uri", None)
        if at_uri is None:
            return
        try:
            post_id = at_uri.split("/")[-1]
        except IndexError:
            return
        post_url = f"https://bsky.app/profile/{self.username}/post/{post_id}"
        show_models.RelatedLink.objects.create(
            content=content,
            description=f"Bluesky post for {content.title}",
            type_id=show_models.RelatedLinkType.BLUESKY_POST,
            title=content.title,
            url=post_url,
        )
