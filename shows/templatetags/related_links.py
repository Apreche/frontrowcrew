from django import template

from shows import models as show_models

register = template.Library()

@register.inclusion_tag("shows/tags/related_links.html")
def related_links(content):
    all_links = show_models.RelatedLink.published.filter(content=content)
    organized_links = {}
    for link in all_links:
        organized_links.setdefault(link.type, [])
        organized_links[link.type].append(link)
    return {"related_links": organized_links}
