from django import http
from django import shortcuts
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from . import models


def homepage(request):
    """ The Homepage """
    template_name = "shows/homepage.html"
    context = {}
    return shortcuts.render(request, template_name, context)


def show_detail(request, show_slug):
    """ The page for a single show with its paginated content """
    ITEMS_PER_PAGE = 10
    template_name = "shows/show_detail.html"
    show = shortcuts.get_object_or_404(models.Show.published, slug=show_slug)
    paginator = Paginator(
        show.published_content,
        ITEMS_PER_PAGE,
        allow_empty_first_page=False,
    )
    if paginator.count == 0:
        raise http.Http404(_("Show has no content."))
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
    """ The page for a single content item """
    template_name = "shows/content_detail.html"
    show = shortcuts.get_object_or_404(models.Show.published, slug=show_slug)
    content = shortcuts.get_object_or_404(
        show.published_content,
        catalog_number=catalog_number
    )
    if (content.slug != content_slug) or (show != content.show):
        return shortcuts.redirect(content, permanent=True)
    things_of_the_day = models.RelatedLink.objects.filter(
        content=content,
        type_id=models.RelatedLinkType.THING_OF_THE_DAY,
    )
    context = {
        "content": content,
        "things_of_the_day": things_of_the_day,
    }
    return shortcuts.render(request, template_name, context)


def totd_list(request):
    """ A list of all the things of the day """
    template_name = "shows/totd_list.html"
    things_of_the_day = models.RelatedLink.published.filter(
        type_id=models.RelatedLinkType.THING_OF_THE_DAY
    )
    if not things_of_the_day:
        raise http.Http404(_("No Things of the Day found."))
    context = {
        "things_of_the_day": things_of_the_day,
    }
    return shortcuts.render(request, template_name, context)
