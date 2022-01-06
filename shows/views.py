from django.core.paginator import Paginator
from django.http.response import Http404
from django import shortcuts
from . import models


def homepage(request):
    template_name = "shows/homepage.html"
    shows = models.Show.objects.all()
    context = {
    }
    return shortcuts.render(request, template_name, context)


def show_detail(request, show_slug):
    ITEMS_PER_PAGE = 10
    template_name = "shows/show_detail.html"
    show = shortcuts.get_object_or_404(models.Show, slug=show_slug)
    content = models.Content.objects.filter(show=show)
    paginator = Paginator(content, ITEMS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    if page.count == 0:
        raise Http404
    context = {
        "show": show,
        "page": page,
    }
    return shortcuts.render(request, template_name, context)


def content_detail(request, show_slug, catalog_number, content_slug=None):
    template_name = "shows/content_detail.html"
    content = shortcuts.get_object_or_404(
        models.Content,
        show__slug=show_slug,
        catalog_number=catalog_number
    )
    if content.slug != content_slug:
        return shortcuts.redirect(content, permanent=True)
    context = {
        'content': content
    }
    return shortcuts.render(request, template_name, context)
