from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete
from . import models as show_models


@receiver(pre_save, sender=show_models.Content)
def render_content_html(sender, instance, **kwargs):
    instance._render_html()
    instance._render_related_links()


@receiver(pre_save, sender=show_models.RelatedLink)
@receiver(post_delete, sender=show_models.RelatedLink)
def render_related_link_html(sender, instance, **kwargs):
    content = instance.content
    content._render_related_links()
