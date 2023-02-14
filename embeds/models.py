from django.db import models


class Service(models.Model):
    YOUTUBE = 1

    name = models.TextField(unique=True)
    embed_template = models.TextField(blank=True, default="")
    uri_template = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name


class Media(models.Model):
    service = models.ForeignKey(
        "embeds.Service", on_delete=models.PROTECT,
    )
    media_id = models.TextField()

    def __str__(self):
        return f"{self.service.name} - {self.media_id}"

    @property
    def embed_code(self):
        return self.service.embed_template.format(
            media_id=self.media_id
        )

    @property
    def external_link(self):
        return self.service.uri_template.format(
            media_id=self.media_id
        )
