from django import template

from shows import models as show_models

register = template.Library()


@register.inclusion_tag("shows/tags/related_links.html")
def related_links(content):
    """ render the related links for a content item in HTML"""
    # We don't need to filter on published because
    # related links are published if the content is published
    all_links = show_models.RelatedLink.objects.filter(content=content)
    organized_links = {}
    for link in all_links:
        organized_links.setdefault(link.type, [])
        organized_links[link.type].append(link)
    return {"related_links": organized_links}
