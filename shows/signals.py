from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from . import models as show_models


@receiver(pre_save, sender=show_models.Content)
def render_content_html(sender, instance, **kwargs):
    instance._render_html()
    instance._render_related_links()


@receiver(post_save, sender=show_models.RelatedLink)
@receiver(post_delete, sender=show_models.RelatedLink)
def render_related_link_html(sender, instance, **kwargs):
    instance.content.save()
