from django import shortcuts
from django.core.paginator import Paginator
from django.http.response import Http404
from . import models


def homepage(request):
    template_name = "shows/homepage.html"
    context = {}
    return shortcuts.render(request, template_name, context)


def show_detail(request, show_slug):
    ITEMS_PER_PAGE = 10
    template_name = "shows/show_detail.html"
    show = shortcuts.get_object_or_404(models.Show.published, slug=show_slug)
    paginator = Paginator(
        show.published_content,
        ITEMS_PER_PAGE,
        allow_empty_first_page=False,
    )
    if paginator.count == 0:
        raise Http404
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(
        page_number
    )
    context = {
        "show": show,
        "page": page,
    }
    return shortcuts.render(request, template_name, context)


def content_detail(request, show_slug, catalog_number, content_slug=None):
    template_name = "shows/content_detail.html"
    show = shortcuts.get_object_or_404(models.Show.published, slug=show_slug)
    content = shortcuts.get_object_or_404(
        show.published_content,
        catalog_number=catalog_number
    )
    if (content.slug != content_slug) or (show != content.show):
        return shortcuts.redirect(content, permanent=True)
    context = {
        'content': content
    }
    return shortcuts.render(request, template_name, context)
